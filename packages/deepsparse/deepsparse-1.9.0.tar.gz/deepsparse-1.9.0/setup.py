# Copyright (c) 2021 - 2025 / Neuralmagic, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import sys
import warnings

from setuptools import setup
from setuptools.command.install import install
from typing import Tuple

class DeprecatedInstallCommand(install):
    def run(self):
        EOL_MESSAGE = """
============================================================================================
'deepsparse' has reached end-of-life and is no longer supported as of June 2025.
See the README for more details: https://github.com/neuralmagic/deepsparse/blob/main/README.md
============================================================================================
        """
        sys.stderr.write(EOL_MESSAGE + "\n")
        sys.exit(1)


def _setup_long_description() -> Tuple[str, str]:
    return open("README.md", "r", encoding="utf-8").read(), "text/markdown"


setup(
    name="deepsparse",
    version="1.9.0",
    author="Neuralmagic, Inc.",
    description=(
        "[DEPRECATED] An inference runtime offering GPU-class performance on CPUs "
        "and APIs to integrate ML into your application"
    ),
    long_description=_setup_long_description()[0],
    long_description_content_type=_setup_long_description()[1],
    keywords=(
        "inference, machine learning, x86, x86_64, avx2, avx512, neural network, "
        "sparse, inference engine, cpu, runtime, deepsparse, computer vision, "
        "object detection, sparsity"
    ),
    license="Neural Magic DeepSparse Community License",
    url="https://github.com/neuralmagic/deepsparse",
    cmdclass={
        'install': DeprecatedInstallCommand,
    },
    python_requires=">=3.8, <3.12",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Operating System :: POSIX :: Linux",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
