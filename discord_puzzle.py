import numpy as np
sqrt = np.sqrt
import sys, os, argparse

def evaluate(expr):
    if len(expr) > 1024:
        return np.inf
    return abs(np.pi - eval(expr))

def build():
    prs = argparse.ArgumentParser()
    prs.add_argument('-file', nargs='*', default=None, help='File(s) such that one line == one entry')
    prs.add_argument('-expr', nargs='*', default=None, help='Command-line expressions as entries')
    prs.add_argument('-no-attribute', action='store_false', help='Do not prepend lines with auto-attribution for source')
    prs.add_argument('-prefix-len', type=int, default=20, help='Amount of eval string to include in output')
    return prs

def load_args(argslike):
    loaded = []
    attributed = []
    if argslike.file is not None:
        for fname in argslike.file:
            if not os.path.exists(fname):
                FNotFound = f"Input file {fname} could not be loaded"  
                raise ValueError(FNotFound)
            with open(fname, 'r') as f:
                old_load_len = len(loaded)
                loaded.extend([_.rstrip() for _ in f.readlines() if len(_.rstrip()) > 0])
                nicename=os.path.basename(fname)
                try:
                    nicename=nicename[:nicename.index('.')]
                except ValueError: # Substring not found
                    pass
                attributed.extend([nicename+":"+str(idx) for idx in range(len(loaded)-old_load_len)])
    if argslike.expr is not None:
        old_load_len = len(loaded)
        loaded.extend([_.rstrip() for _ in argslike.expr if len(_.rstrip()) > 0])
        attributed.extend(["COMMANDLINE:"+str(idx) for idx in range(len(loaded)-old_load_len)])
    if not argslike.attribute:
        attributed = None
    return loaded, attributed

def parse(prs, args=None):
    if args is None:
        args = prs.parse_args()
    if args.file is None and args.expr is None:
        NoExprs = "No expressions supplied (use -file and/or -expr)"
        raise ValueError(NoExprs)
    args.loaded, args.attributed = load_args(args)
    if len(args.loaded) == 0:
        EmptyExprs = "Supplied expressions are empty"
        raise ValueError(EmptyExprs)
    args.kwargs = {'prefix_len': args.prefix_len}
    args.attribute = not args.no_attribute
    return args

def argpad_fn(eval_str, attr_str=None, **kwargs):
    prefix = attr_str+"\t" if attr_str is not None else ""
    id_str = eval_str[:kwargs['prefix_len']] if 'prefix_len' in kwargs.keys() else eval_str[:20]
    if 'prefix_len' in kwargs and len(id_str) < kwargs['prefix_len']:
      id_str += ' '*(kwargs['prefix_len']-len(eval_str))
    return f"{prefix}{id_str}..."

def eval_loop(iterable_evals, iterable_attrs=None, argpad=None, **kwargs):
    if argpad is None:
        argpad = argpad_fn
    if iterable_attrs is None:
        iterable_attrs = [None for _ in range(len(iterable_evals))]
    scores = {}  
    for idx, evalable in enumerate(iterable_evals):
        scores[idx] = evaluate(evalable)
    score_order = np.argsort(list(scores.values()))
    for rank, idx in enumerate(score_order):
        print(f"Rank {rank+1}: {argpad(iterable_evals[idx], iterable_attrs[idx], **kwargs)} = {scores[idx]}")

if __name__ == '__main__':
    args = parse(build())  
    eval_loop(args.loaded, args.attributed, **args.kwargs)

