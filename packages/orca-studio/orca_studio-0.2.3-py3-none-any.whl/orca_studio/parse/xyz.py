from orca_studio.parse.common import extract_table_lines, find_section_starts

TABLE_HEADER = "CARTESIAN COORDINATES (ANGSTROEM)"
TABLE_START_OFFSET = 2


def xyz(lines: list[str]) -> str:
    """Parse the last cartesian coordinates (angstrom) in the output as a valid XYZ string."""
    xyz_blocks = find_section_starts(lines, TABLE_HEADER, TABLE_START_OFFSET)

    xyz_block = extract_table_lines(lines, xyz_blocks[-1])

    xyz = f"{len(xyz_block)}\n\n" + "\n".join(xyz_block)
    return xyz
