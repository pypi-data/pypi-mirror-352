from pathlib import Path


class SWATWriteCliFiles:
    """Generate .cli files for the SWAT model."""

    def __init__(
        self,
        folder_path: str,
        station_names: list[str],
        add_default_extension: bool = True,
    ):
        """Initialize the SWATWriteCliFiles class.

        Args:
            folder_path (str): Path where to save the files.
            station_names (list[str]): List of the station names (usually without extension).
            add_default_extension (bool): Add the default extension to the station names, e.g., Station_1 -> Station_1.hmd.
        """
        self.folder_path = folder_path
        self.station_names = station_names
        self.add_default_extension = add_default_extension

    def write_tmp(self):
        """Write tmp.cli file

        Returns:
            tuple[str, str]: Tuple with the file path and the file data.

        """
        return self._write_cli_file("tmp", "tmp.cli: Temperature file names")

    def write_hmd(self):
        """Write hmd.cli file

        Returns:
            tuple[str, str]: Tuple with the file path and the file data.
        """
        return self._write_cli_file("hmd", "hmd.cli: Relative humidity file names")

    def write_slr(self):
        """Write slr.cli file

        Returns:
            tuple[str, str]: Tuple with the file path and the file data.
        """
        return self._write_cli_file("slr", "slr.cli: Solar radiation file names")

    def write_pcp(self):
        """Write pcp.cli file

        Returns:
            tuple[str, str]: Tuple with the file path and the file data.
        """
        return self._write_cli_file("pcp", "pcp.cli: Precipitation file names")

    def write_wnd(self):
        """Write wnd.cli file

        Returns:
            tuple[str, str]: Tuple with the file path and the file data.
        """
        return self._write_cli_file("wnd", "wnd.cli: Wind speed file names")

    def _write_cli_file(self, type: str, headline: str) -> tuple[str, str]:
        """
        Creates and writes a .cli file for the specified type.

        Args:
            type (str): Type of file - 'tmp', 'hmd', 'slr', 'pcp', 'wnd'.
            headline (str): Text to write to the first line in the cli file.

        Returns:
            tuple[str, str]: Tuple with the file path and the file data.
        """
        if type not in ["tmp", "hmd", "slr", "pcp", "wnd"]:
            raise ValueError(f"Invalid type: {type}")

        file_name = f"{type}.cli"
        file_path = Path(self.folder_path) / file_name

        station_names = (
            self.station_names
            if self.add_default_extension == False
            else [s + f".{type}" for s in self.station_names]
        )

        with open(file_path, "w") as f:
            f.write(f"{headline} - Written by WWTToolbox\n")
            f.write("filename\n")
            for station_name in station_names:
                f.write(f"{station_name}\n")

        return file_path, file_name
