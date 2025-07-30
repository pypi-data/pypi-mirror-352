from typing import Union, Any, ParamSpec, Callable
import asyncio
import orjson
from tqdm import tqdm
import pandas as pd
from .abstract import BaseDataframe
from ...exceptions import ComponentError, DataNotFound

P = ParamSpec("P")


def is_empty(obj):
    """check_empty.
    Check if a basic object is empty or not.
    """
    if isinstance(obj, pd.DataFrame):
        return True if obj.empty else False
    else:
        return bool(not obj)


class PandasDataframe(BaseDataframe):
    """PandasDataframe.

    Converts any result into a Pandas DataFrame.
    """
    chunk_size: int = 100
    task_parts: int = 10

    async def create_dataframe(
        self,
        result: Union[dict, bytes, Any],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> Any:
        """
        Converts any result into a Pandas DataFrame.

        :param result: The result data to be converted into a Pandas DataFrame.
        :return: A DataFrame containing the result data.
        """
        if is_empty(result):
            raise DataNotFound("DataFrame: No Data was Found.")
        try:
            if isinstance(result, str):
                try:
                    result = orjson.loads(result)
                except Exception:
                    pass
            if isinstance(result, dict):
                result = [result]
            df = pd.DataFrame(result, **kwargs)
            # Attempt to infer better dtypes for object columns.
            df.infer_objects()
            columns = list(df.columns)
            if hasattr(self, "infer_types"):
                df = df.convert_dtypes(convert_string=self.to_string)
            if hasattr(self, "infer_types"):
                df = df.convert_dtypes()
            if hasattr(self, "drop_empty"):
                df.dropna(axis=1, how="all", inplace=True)
                df.dropna(axis=0, how="all", inplace=True)
            if hasattr(self, "dropna"):
                df.dropna(subset=self.dropna, how="all", inplace=True)
            numrows = len(df.index)
            try:
                self._variables["_numRows_"] = numrows
                self.add_metric("NUM_ROWS", numrows)
                self.add_metric("NUM_COLS", len(columns))
            except Exception:
                pass
            return df
        except Exception as err:
            raise ComponentError(
                f"Error Creating Dataframe: {err!s}"
            )

    async def from_csv(
        self, result: str, *args: P.args, **kwargs: P.kwargs
    ) -> Any:
        """
        Converts a Comma-Separated CSV into a Pandas DataFrame.

        :param result: The result data to be converted into a Pandas DataFrame.
        :return: A DataFrame containing the result data.
        """
        if is_empty(result):
            raise DataNotFound("DataFrame: No Data was Found.")
        try:
            df = pd.read_csv(result, encoding="utf-8", **kwargs)
            # Attempt to infer better dtypes for object columns.
            df.infer_objects()
            columns = list(df.columns)
            if hasattr(self, "infer_types"):
                df = df.convert_dtypes(convert_string=self.to_string)
            if hasattr(self, "infer_types"):
                df = df.convert_dtypes()
            if hasattr(self, "drop_empty"):
                df.dropna(axis=1, how="all", inplace=True)
                df.dropna(axis=0, how="all", inplace=True)
            if hasattr(self, "dropna"):
                df.dropna(subset=self.dropna, how="all", inplace=True)
            numrows = len(df.index)
            try:
                self._variables["_numRows_"] = numrows
                self.add_metric("NUM_ROWS", numrows)
                self.add_metric("NUM_COLS", len(columns))
            except Exception:
                pass
            return df
        except Exception as err:
            raise ComponentError(f"Error Creating Dataframe: {err!s}")

    def column_exists(self, column: str):
        """Returns True if the column exists in the DataFrame."""
        if column not in self.data.columns:
            self._logger.warning(
                f"Column {column} does not exist in the dataframe"
            )
            self.data[column] = None
            return False
        return True

    def _create_tasks(self, dataframe: pd.DataFrame, func: Union[str, Callable], **kwargs) -> list:
        """
        Create tasks for processing the DataFrame.

        :param dataframe: The DataFrame to process.
        :param
        func: The function to apply to each row.
        :return: A list of tasks.
        """
        if isinstance(func, str):
            func = getattr(self, func)
            if not callable(func):
                raise ValueError(f"Function {func} is not callable.")
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError(f"Dataframe {dataframe} is not a DataFrame.")
        if dataframe.empty:
            raise ValueError(f"Dataframe {dataframe} is empty.")
        tasks = []
        for idx, row in dataframe.iterrows():
            tasks.append(func(row, idx, **kwargs))
        return tasks

    def split_parts(self, task_list, num_parts: int = 5) -> list:
        part_size = len(task_list) // num_parts
        remainder = len(task_list) % num_parts
        parts = []
        start = 0
        for i in range(num_parts):
            # Distribute the remainder across the first `remainder` parts
            end = start + part_size + (1 if i < remainder else 0)
            parts.append(task_list[start:end])
            start = end
        return parts

    async def _processing_tasks(self, tasks: list, description: str = ': Processing :') -> pd.DataFrame:
        """Process tasks concurrently."""
        results = []
        total_tasks = len(tasks)
        pbar = tqdm(total=total_tasks, desc=description)
        try:
            for chunk in self.split_parts(tasks, self.task_parts):
                # ─── Wrap every coroutine in this chunk into a Task ───
                pending = [asyncio.create_task(coro) for coro in chunk]
                # Schedule only this chunk concurrently:
                for coro in asyncio.as_completed(pending):
                    res = await coro
                    results.append(res)
                    pbar.update(1)
        finally:
            pbar.close()
        return results
