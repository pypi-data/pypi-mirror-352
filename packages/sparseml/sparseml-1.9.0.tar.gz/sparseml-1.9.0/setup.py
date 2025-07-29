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
'sparseml' has reached end-of-life and is no longer supported as of June 2025.
See the README for more details: https://github.com/neuralmagic/sparseml/blob/main/README.md
============================================================================================
        """
        sys.stderr.write(EOL_MESSAGE + "\n")
        sys.exit(1)


def _setup_long_description() -> Tuple[str, str]:
    return open("README.md", "r", encoding="utf-8").read(), "text/markdown"


setup(
    name="sparseml",
    version="1.9.0",
    author="Neuralmagic, Inc.",
    description=(
        "[DEPRECATED] Libraries for applying sparsification recipes to neural networks with a "
        "few lines of code, enabling faster and smaller models"
    ),
    long_description=_setup_long_description()[0],
    long_description_content_type=_setup_long_description()[1],
    keywords=(
        "inference, machine learning, neural network, computer vision, nlp, cv, "
        "deep learning, torch, pytorch, tensorflow, keras, sparsity, pruning, "
        "deep learning libraries, onnx, quantization, automl"
    ),
    license="Apache",
    url="https://github.com/neuralmagic/sparseml",
    cmdclass={
        'install': DeprecatedInstallCommand,
    },
    python_requires=">=3.8.0,<3.12",
    classifiers=[
        "Development Status :: 7 - Inactive",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
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
