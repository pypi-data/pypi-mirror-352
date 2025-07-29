import io
import logging
from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict, List, NamedTuple

import numpy as np
import pandas as pd
from pydantic import BaseModel, Field, field_validator, model_validator

from synthera.protocols import SyntheraClientProtocol

_logger: logging.Logger = logging.getLogger(__name__)


class ModelsLabel(BaseModel):
    model_label: str


class ModelLabelsResponse(BaseModel):
    model_labels: List[str]


class ModelMetadata(BaseModel):
    model_label: str
    universe: str
    curve_labels: list[str]
    start_date_training: str
    end_date_training: str
    simulation_steps: int
    conditional_steps: int
    tenors: list[float]


class ModelMetadataResponse(BaseModel):
    metadata: ModelMetadata


class SimulationPastDateRequest(BaseModel):
    model_label: str = Field(
        ...,  # Make it required
        description="Model label",
        examples=["YieldGAN-vV-z0"],
        min_length=1,
    )
    curve_labels: List[str] = Field(
        ...,  # Make it required
        description="List of yield curve labels",
        examples=["USA", "GBR", "DEU"],
        min_length=1,  # Ensure at least one curve name is provided
    )
    no_of_samples: int = Field(
        ...,  # Make it required
        description="Number of samples",
        examples=[100, 1000, 10000],
        gt=0,
    )
    no_of_days: int = Field(
        ...,  # Make it required
        description="Number of days",
        examples=[3, 30, 120],
        gt=0,
    )
    reference_date: str = Field(
        ...,  # Make it required
        description="Reference date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",  # Regex pattern for YYYY-MM-DD
    )
    return_conditional: bool = Field(
        default=False,  # Provide default value
        description="Return conditional flag",
    )

    @field_validator("reference_date")
    def validate_date_format(cls, v: str) -> str:
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Must be YYYY-MM-DD")
        return v

    @model_validator(mode="after")
    def validate_model(self) -> "SimulationPastDateRequest":
        # Ensure reference date is not in the future
        if datetime.strptime(self.reference_date, "%Y-%m-%d") > datetime.now():
            raise ValueError("reference_date cannot be in the future")

        # Validate total data points don't exceed reasonable limit
        total_points = self.no_of_samples * self.no_of_days * len(self.curve_labels)
        if total_points > 100_000_000:  # 100 million points limit
            raise ValueError(
                f"Total data points ({total_points}) exceeds maximum limit"
            )

        return self


class SimulationPastDateOutput(BaseModel):
    curve_label: str
    data: str


class SimulationPastDateMetadata(ModelMetadata):
    """Metadata for simulation past date request

    Inherits from ModelMetadata: adds reference_date.
    """

    reference_date: str


class SimulationPastDateResponse(BaseModel):
    outputs: List[SimulationPastDateOutput]
    metadata: SimulationPastDateMetadata


class SimulationPastDateResults(NamedTuple):
    dataframes: OrderedDict[str, pd.DataFrame]
    names: List[str]
    column_names: List[str]
    ndarray: np.ndarray
    metadata: Dict[str, Any]


class FixedIncome:
    fixed_income_endpoint: str = "fixed-income"
    simulation_past_date_endpoint: str = f"{fixed_income_endpoint}/simulation/past-date"
    model_labels_endpoint: str = f"{fixed_income_endpoint}/models/labels"
    model_metadata_endpoint: str = f"{fixed_income_endpoint}/models/metadata"

    def __init__(self, client: SyntheraClientProtocol) -> None:
        self.client: SyntheraClientProtocol = client

    def _decode_to_df(self, encoded_data: str) -> pd.DataFrame:
        """Decode a hex-encoded parquet file string into a pandas DataFrame."""
        try:
            parquet_bytes: bytes = bytes.fromhex(encoded_data)
            buffer: io.BytesIO = io.BytesIO(parquet_bytes)
            df: pd.DataFrame = pd.read_parquet(buffer, engine="pyarrow")
        except Exception as e:
            raise ValueError(f"Failed to decode data: {e}")
        return df

    def simulation_past_date(self, params: dict) -> SimulationPastDateResults:
        """Simulate yield curves for past dates."""
        # pre-processing
        request: SimulationPastDateRequest = SimulationPastDateRequest.model_validate(
            params
        )

        _logger.info(
            f"Requesting simulation of yield curves for past dates: {request.model_dump()}"
        )

        # make request
        response: dict = self.client.make_post_request(
            endpoint=self.simulation_past_date_endpoint,
            payload=request.model_dump(),
        )

        response: SimulationPastDateResponse = (
            SimulationPastDateResponse.model_validate(response)
        )

        # post-processing
        dataframes: OrderedDict[str, pd.DataFrame] = OrderedDict()
        for output in response.outputs:
            df: pd.DataFrame = self._decode_to_df(output.data)
            df["IDX"] = pd.to_datetime(df["IDX"], unit="s")
            df["SAMPLE"] = df["SAMPLE"].astype(int)
            dataframes.update({output.curve_label: df})

        array: np.ndarray = np.concatenate(
            [
                df.values.reshape(request.no_of_samples, 1, -1, df.values.shape[1])
                for key, df in dataframes.items()
            ],
            axis=1,
        )

        return SimulationPastDateResults(
            dataframes=dataframes,
            names=list(dataframes.keys()),
            ndarray=array,
            column_names=list(list(dataframes.values())[0].columns),
            metadata=response.metadata.model_dump(),
        )

    def model_labels(self) -> List[str]:
        """Get the list of model labels."""
        response: dict = self.client.make_get_request(
            endpoint=self.model_labels_endpoint,
        )
        response: ModelLabelsResponse = ModelLabelsResponse.model_validate(response)
        return response.model_labels

    def model_metadata(self, model_label: str) -> ModelMetadata:
        """Get the metadata for a model."""
        request: ModelsLabel = ModelsLabel(model_label=model_label)
        response: dict = self.client.make_get_request(
            endpoint=self.model_metadata_endpoint,
            params=request.model_dump(),
        )
        response: ModelMetadataResponse = ModelMetadataResponse.model_validate(response)
        return response.metadata
