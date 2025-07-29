# Copyright 2024 Natan Junges <natanajunges@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import subprocess
import sys

from cogapp import Cog

included: bool = False

LT: str = "<"
GT: str = ">"

def bool(value: str) -> bool:
    return value == "True"

def name(filename: str) -> str:
    return os.path.splitext(os.path.basename(filename))[0]

def format(input_: str, **kwargs: str) -> str:
    return eval(f'f"""{input_}"""', kwargs)

def include_static(filename: str) -> str:
    with open(filename) as file:
        return file.read().rstrip()

def include_generate(filename: str, **kwargs: str) -> str:
    args = ["cog", "-d", "-p", "import cogssg as ssg; ssg.included = True"]

    for arg in kwargs.items():
        args.append("-D")
        args.append(f"{arg[0]}={arg[1]}")

    args.append(filename)
    return subprocess.run(args, capture_output=True, check=True, encoding="UTF-8").stdout.rstrip()

def main():
    return Cog().main(["cog", "-p", "import cogssg as ssg", "-r", sys.argv[1]])
