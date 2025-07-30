#!/usr/bin/env python3
#     The Certora Prover
#     Copyright (C) 2025  Certora Ltd.
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, version 3 of the License.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <https://www.gnu.org/licenses/>.


import sys
from pathlib import Path
from rich.console import Console


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

import CertoraProver.certoraContextAttributes as Attrs
from Shared import certoraUtils as Util
from certoraRun import run_certora, CertoraRunResult, CertoraFoundViolations

from typing import List, Optional


def run_ranger(args: List[str]) -> Optional[CertoraRunResult]:
    return run_certora(args, Attrs.RangerAttributes, prover_cmd=sys.argv[0])

def entry_point() -> None:
    try:
        run_ranger(sys.argv[1:])
        sys.exit(0)
    except KeyboardInterrupt:
        Console().print("[bold red]\nInterrupted by user")
        sys.exit(1)
    except Util.TestResultsReady:
        print("reached checkpoint")
        sys.exit(0)
    except CertoraFoundViolations as e:
        try:
            assert e.results
            print(f"report url: {e.results.rule_report_link}")
        except Exception:
            pass
        Console().print("[bold red]\nViolations were found\n")
        sys.exit(1)
    except Util.CertoraUserInputError as e:
        if e.orig:
            print(f"\n{str(e.orig).strip()}")
        if e.more_info:
            print(f"\n{e.more_info.strip()}")
        Console().print(f"[bold red]\n{e}\n")
        sys.exit(1)

    except Util.ExitException as e:
        Console().print(f"[bold red]{e}")
        sys.exit(e.exit_code)

    except Exception as e:
        Console().print(f"[bold red]{e}")
        sys.exit(1)

if __name__ == '__main__':
    entry_point()
