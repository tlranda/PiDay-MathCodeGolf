#!/usr/bin/python3
import os
import argparse
import warnings
try:
    import numpy as np
except ImportError as e:
    print("You may need to load a virtualenv with Numpy or install it via `pip3 install --user numpy`")
    raise e
# Add to global namespace such that entries may call this function
sqrt = np.sqrt

# !! General users: run `python3 discord_puzzle.py --help` for instructions


def evaluate(expr: str) -> float:
    """
        Core evaluation function that scores a mathematical string

        Args:
          expr [str]: Eval-ready mathematic string
        Returns:
          float: Error relative to numpy's pi constant
    """
    if len(expr) > 1024:
        return np.inf
    return abs(np.pi - eval(expr))

def build() -> argparse.ArgumentParser:
    """
        Returns ArgParser object that defines CLI and controls
    """
    prs = argparse.ArgumentParser()
    prs.add_argument('-file', nargs='*', default=None, help='File(s) such that one line == one entry')
    prs.add_argument('-expr', nargs='*', default=None, help='Command-line expressions as entries')
    prs.add_argument('-no-attribute', action='store_true', help='Do not prepend lines with auto-attribution for source')
    prs.add_argument('-eval-len', type=int, default=20, help='Amount of eval string to include in output')
    prs.add_argument('-float-ok', action='store_true', help='Allow floating point values (naive check for "." character) in entries')
    return prs

def entry_handler(exprList: list[str], attr_name: str, float_ok: bool) -> tuple[list[str], list[str]]:
    """
        Return accepted entries with attribution

        Args:
            exprList [list: str]: Expressions to consider
            attr_name [str]: Classification for this group
            float_ok [bool]: Disallow expressions if they appear to contain floating point values

        Returns:
            add [list: str]: Permitted expressions
            attributed [list: str]: Proper identifiers for expression sources
    """
    add = []
    add_dx = []
    # _.rstrip() removes any right-side whitespace (usually \n character)
    for idx, entry in enumerate([_.rstrip() for _ in exprList]):
        if len(entry) == 0:
            continue
        if float_ok or '.' not in entry:
            add.append(entry)
            add_dx.append(idx)
        else:
            warnings.warn(f"{attr_name}:{idx} disallowed for using a floating point value", Warning)  
    attributed = [f"{attr_name}:{idx}" for idx in add_dx]
    return add, attributed

def load_args(argslike: object) -> tuple[list[str], list[str]]:
    """
        Converts entries supplied directly over CLI or via file name into ready objects

        Args:
            argslike: A namespace (x.attr -- addressable) object with the following attributes:
                * file [list: str | None]: Paths to read and convert
                * expr [list: str | None]: Direct entires to consider
                * float_ok [bool]: Decides if entries containing potential floating-point values are rejected or not
                * attributed [bool]: Determines if second return is None or a list of strings to narrow down source of entries

        Returns:
            loaded: A list of accepted eval-able strings
            attributed: A list of attributions for the source of each accepted string
    """
    loaded = []
    attributed = []
    # Handle files first
    if argslike.file is not None:
        for fname in argslike.file:
            if not os.path.exists(fname):
                FNotFound = f"Input file {fname} could not be loaded"  
                raise ValueError(FNotFound)
            with open(fname, 'r') as f:
                nicename=os.path.basename(fname)
                try:
                    nicename=nicename[:nicename.rindex('.')]
                except ValueError: # Substring not found (file has no extension)
                    pass
                add, attribs = entry_handler([_ for _ in f.readlines()], nicename, argslike.float_ok)
                loaded.extend(add)
                attributed.extend(attribs)
    # Handle direct CLI arguments second
    if argslike.expr is not None:
        add, attribs = entry_handler(argslike.expr, "COMMANDLINE", argslike.float_ok)
        loaded.extend(add)
        attributed.extend(attribs)
    # Maybe-drop all attributions here as they would need to be generated for entry_handler warnings regardless
    if not argslike.attributed:
        attributed = None
    return loaded, attributed

def parse(prs: argparse.ArgumentParser, args: list[str] = None) -> argparse.Namespace:
    """
        Interpret arguments (may be from sys.argv--default, or hand-specified) and return them.
        Also performs any relevant validity checks for CLI parameters

        Args:
            prs: argparse object for handling CLI
            args: Optional list to override CLI fetch (argparse may not fetch more than once per runtime)
    """
    if args is None:
        args = prs.parse_args()
    args.attributed = not args.no_attribute
    args.kwargs = {'eval_len': args.eval_len} # Can bundle more things later on

    # Validity checks
    if args.file is None and args.expr is None:
        NoExprs = "No expressions supplied (use -file and/or -expr)"
        raise ValueError(NoExprs)
    # Load, extra validity checks
    args.loaded, args.attributed = load_args(args)
    if len(args.loaded) == 0:
        EmptyExprs = "Supplied expressions are empty"
        raise ValueError(EmptyExprs)
    return args

def argpad_fn(eval_str: str, attr_str: str = None, **kwargs) -> str:
    """
        Combines strings to make them presentable

        Args:
            eval_str: The math string that produced a result
            attr_str: Optional string to claim the eval string's source
            kwargs: Bonus options currently include
                * attr_max: Helps define consistent padding for attribute portions
                * eval_len: Max number of characters to include from eval_str
    """
    # Show attribution
    prefix = attr_str if attr_str is not None else ""
    if len(prefix) < kwargs['attr_max']:
        prefix += ' '*(kwargs['attr_max']-len(prefix))
    if attr_str is not None:
        prefix+='\t'

    # Show eval string
    id_str = eval_str[:kwargs['eval_len']] if 'eval_len' in kwargs.keys() else eval_str[:20]
    if 'eval_len' in kwargs and len(id_str) < kwargs['eval_len']:
      id_str += ' '*(kwargs['eval_len']-len(eval_str))

    # Return union with ...
    return f"{prefix}{id_str}..."

def eval_loop(iterable_evals: list[str], iterable_attrs: list[str] = None, argpad: callable = None, **kwargs) -> None:
    """
        Parse given lists and produce a ranked list based on accuracy

        Args:
            iterable_evals: List of evaluable strings to score
            iterable_attrs: Optional list of name sources to show
            argpad: Callable function to generate names for eval strings and attributions
            kwargs: Forwarded to argpad
    """
    # Override with default string-ifier
    if argpad is None:
        argpad = argpad_fn
    # Validity check
    if iterable_attrs is None:
        iterable_attrs = [None for _ in range(len(iterable_evals))]
        kwargs['attr_max'] = 0
    else:
        kwargs['attr_max'] = max([len(_) for _ in iterable_attrs])

    # Generate scores
    scores = {}  
    for idx, evalable in enumerate(iterable_evals):
        scores[idx] = evaluate(evalable)
    # Output in sorted order
    score_order = np.argsort(list(scores.values()))
    for rank, idx in enumerate(score_order):
        print(f"Rank {rank+1}: {argpad(iterable_evals[idx], iterable_attrs[idx], **kwargs)} = {scores[idx]}")

if __name__ == '__main__':
    args = parse(build())  
    eval_loop(args.loaded, args.attributed, **args.kwargs)

