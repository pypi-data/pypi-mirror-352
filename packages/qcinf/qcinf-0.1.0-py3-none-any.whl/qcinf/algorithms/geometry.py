"""Top-level functions for geometry-related algorithms."""

from typing import Callable

from qcio import ConformerSearchResults, Structure

from qcinf._backends import rdkit

_RMSD_BACKEND_MAP: dict[str, Callable[..., float]] = {
    "rdkit": rdkit._rmsd_rdkit,
}


def rmsd(
    struct1: Structure,
    struct2: Structure,
    *,
    backend: str = "rdkit",
    **kwargs,
) -> float:
    """Calculate the root mean square deviation (RMSD) between two structures.

    Args:
        struct1: The first structure.
        struct2: The second structure.
        backend: The backend to use for the RMSD calculation. Can be 'rdkit'.
        **kwargs: Backend-specific additional keywords to pass to the RMSD calculation
            function. This can include options like 'symmetry' for symmetry-based RMSD
            calculations. The specific options depend on the backend used. See
            [qcinf._backends.<backend>._rmsd_<backend>] for details.

    Returns:
        The RMSD value between the two structures.

    Raises:
        ValueError: If the backend is not one of the supported options.
    """
    try:
        fn = _RMSD_BACKEND_MAP[backend.lower()]
    except KeyError as e:
        raise ValueError(
            f"Unknown backend '{backend}'.  Known: {list(_RMSD_BACKEND_MAP)}"
        ) from e
    return fn(struct1, struct2, **kwargs)


_ALIGN_BACKEND_MAP: dict[str, Callable[..., tuple[Structure, float]]] = {
    "rdkit": rdkit._align_rdkit,
}


def align(
    struct: Structure,
    refstruct: Structure,
    *,
    backend: str = "rdkit",
    symmetry: bool = False,
    **kwargs,
) -> tuple[Structure, float]:
    """Align a structure to a reference structure.

    Args:
        struct: The structure to align.
        refstruct: The reference structure to align against.
        backend: The backend to use for the alignment. Can be 'rdkit'.
        symmetry: Whether to use symmetry in the alignment. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the alignment function.

    Returns:
        A tuple containing the RMSD and the aligned structure.
    """
    try:
        fn = _ALIGN_BACKEND_MAP[backend.lower()]
    except KeyError as e:
        raise ValueError(
            f"Unknown backend '{backend}'.  Known: {list(_ALIGN_BACKEND_MAP)}"
        ) from e
    return fn(struct, refstruct, symmetry=symmetry, **kwargs)


def filter_conformers(
    csr: ConformerSearchResults,
    *,
    backend: str = "rdkit",
    threshold: float = 1.0,
    **rmsd_kwargs,
) -> ConformerSearchResults:
    """Filter conformers based on RMSD threshold.

    Args:
        csr: The ConformerSearchResults object to filter.
        backend: The backend to use for the RMSD calculation. Can be 'rdkit'.
        threshold: The RMSD threshold for filtering in Bohr. Defaults to 1.0 Bohr
            (0.53 Angstrom).
        **rmsd_kwargs: Additional keyword arguments to pass to the RMSD calculation
            function. This can include options like 'symmetry' for symmetry-based RMSD
            calculations. The specific options depend on the backend used. See
            [qcinf._backends.<backend>._rmsd_<backend>] for details.

    Returns:
        A new ConformerSearchResults object containing only the conformers that
        meet the RMSD threshold.
    """
    filtered = set()
    for i in range(len(csr.conformers)):
        if i not in filtered:
            for j in range(i + 1, len(csr.conformers)):
                if (
                    rmsd(
                        csr.conformers[i],
                        csr.conformers[j],
                        backend=backend,
                        **rmsd_kwargs,
                    )
                    < threshold
                ):
                    filtered.add(j)

    keep_indices = [i for i in range(len(csr.conformers)) if i not in filtered]
    return ConformerSearchResults(
        conformers=[csr.conformers[i] for i in keep_indices],
        conformer_energies=csr.conformer_energies_relative[keep_indices],
    )
