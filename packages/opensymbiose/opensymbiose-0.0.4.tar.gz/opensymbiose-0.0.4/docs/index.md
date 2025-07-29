---
title: Home
description: OpenSymbiose
hide:
  - navigation
---

# OpenSymbiose: Open Source Biotechnology AI Agent

OpenSymbiose is an open-source biotechnology / biology research AI agent designed to support researchers.

[DOCUMENTATION](https://lambda-science.github.io/OpenSymbiose/) - [DEMO ON HUGGINGFACE](https://huggingface.co/spaces/corentinm7/opensymbiose) - [CODE REPO](https://github.com/lambda-science/OpenSymbiose)

Creator and Maintainer: [**Corentin Meyer**, PhD](https://cmeyer.fr/) - <contact@cmeyer.fr>

## Installation

If you want just to interact with it, an online demo is available
on [HuggingFace](https://huggingface.co/spaces/corentinm7/opensymbiose)

**Note:** In every-case you will need an environment variable or a .env file with your `MISTRAL_API_KEY` secret.

- Install from PyPi: `pip install opensymbiose`
    - Locally: Run in your terminal `opensymbiose` it will boot the gradio app
    - In Docker: `make dockerbuild && make dockerrun` to run in Docker.
- From GitHub: clone the repository and run `make dev`. It will launch the Gradio app with hot-reloading.
