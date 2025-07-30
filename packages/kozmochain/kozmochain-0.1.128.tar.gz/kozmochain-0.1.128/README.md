<p align="center">
  <img src="docs/logo/dark.svg" width="400px" alt="Kozmochain Logo">
</p>

<p align="center">
  <a href="https://pypi.org/project/kozmochain/">
    <img src="https://img.shields.io/pypi/v/kozmochain" alt="PyPI">
  </a>
  <a href="https://pepy.tech/project/kozmochain">
    <img src="https://static.pepy.tech/badge/kozmochain" alt="Downloads">
  </a>
  <a href="https://digi-trans.org/slack">
    <img src="https://img.shields.io/badge/slack-kozmochain-brightgreen.svg?logo=slack" alt="Slack">
  </a>
  <a href="https://digi-trans.org/discord">
    <img src="https://dcbadge.vercel.app/api/server/6PzXDgEjG5?style=flat" alt="Discord">
  </a>
  <a href="https://twitter.com/kozmochain">
    <img src="https://img.shields.io/twitter/follow/kozmochain" alt="Twitter">
  </a>
  <a href="https://colab.research.google.com/drive/138lMWhENGeEu7Q1-6lNbNTHGLZXBBz_B?usp=sharing">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open in Colab">
  </a>
  <a href="https://codecov.io/gh/kozmochain/kozmochain">
    <img src="https://codecov.io/gh/kozmochain/kozmochain/graph/badge.svg?token=EMRRHZXW1Q" alt="codecov">
  </a>
</p>

<hr />

## What is Kozmochain?

Kozmochain is an Open Source Framework for personalizing LLM responses. It makes it easy to create and deploy personalized AI apps. At its core, Kozmochain follows the design principle of being *"Conventional but Configurable"* to serve both software engineers and machine learning engineers.

Kozmochain streamlines the creation of personalized LLM applications, offering a seamless process for managing various types of unstructured data. It efficiently segments data into manageable chunks, generates relevant embeddings, and stores them in a vector database for optimized retrieval. With a suite of diverse APIs, it enables users to extract contextual information, find precise answers, or engage in interactive chat conversations, all tailored to their own data.

## 🔧 Quick install

### Python API

```bash
pip install kozmochain
```

## ✨ Live demo

Checkout the [Chat with PDF](https://digi-trans.org/demo/chat-pdf) live demo we created using Kozmochain. You can find the source code [here](https://github.com/digitranslab/kozmodb/tree/main/kozmochain/examples/chat-pdf).

## 🔍 Usage

<!-- Demo GIF or Image -->
<p align="center">
  <img src="docs/images/cover.gif" width="900px" alt="Kozmochain Demo">
</p>

For example, you can create an Elon Musk bot using the following code:

```python
import os
from kozmochain import App

# Create a bot instance
os.environ["OPENAI_API_KEY"] = "<YOUR_API_KEY>"
app = App()

# Embed online resources
app.add("https://en.wikipedia.org/wiki/Elon_Musk")
app.add("https://www.forbes.com/profile/elon-musk")

# Query the app
app.query("How many companies does Elon Musk run and name those?")
# Answer: Elon Musk currently runs several companies. As of my knowledge, he is the CEO and lead designer of SpaceX, the CEO and product architect of Tesla, Inc., the CEO and founder of Neuralink, and the CEO and founder of The Boring Company. However, please note that this information may change over time, so it's always good to verify the latest updates.
```

You can also try it in your browser with Google Colab:

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/17ON1LPonnXAtLaZEebnOktstB_1cJJmh?usp=sharing)

## 📖 Documentation
Comprehensive guides and API documentation are available to help you get the most out of Kozmochain:

- [Introduction](https://docs.digi-trans.org/get-started/introduction#what-is-kozmochain)
- [Getting Started](https://docs.digi-trans.org/get-started/quickstart)
- [Examples](https://docs.digi-trans.org/examples)
- [Supported data types](https://docs.digi-trans.org/components/data-sources/overview)

## 🔗 Join the Community

* Connect with fellow developers by joining our [Slack Community](https://digi-trans.org/slack) or [Discord Community](https://digi-trans.org/discord).

* Dive into [GitHub Discussions](https://github.com/digitranslab/kozmochain/discussions), ask questions, or share your experiences.

## 🤝 Schedule a 1-on-1 Session

Book a [1-on-1 Session](https://cal.com/mobenchio/ec) with the founders, to discuss any issues, provide feedback, or explore how we can improve Kozmochain for you.

## 🌐 Contributing

Contributions are welcome! Please check out the issues on the repository, and feel free to open a pull request.
For more information, please see the [contributing guidelines](CONTRIBUTING.md).

For more reference, please go through [Development Guide](https://docs.digi-trans.org/contribution/dev) and [Documentation Guide](https://docs.digi-trans.org/contribution/docs).

<a href="https://github.com/digitranslab/kozmochain/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=kozmochain/kozmochain" />
</a>

## Anonymous Telemetry

We collect anonymous usage metrics to enhance our package's quality and user experience. This includes data like feature usage frequency and system info, but never personal details. The data helps us prioritize improvements and ensure compatibility. If you wish to opt-out, set the environment variable `EC_TELEMETRY=false`. We prioritize data security and don't share this data externally.

## Citation

If you utilize this repository, please consider citing it with:

```
@misc{kozmochain,
  author = {Mohamed Ben Chaliah, Mohamed Ben Chaliah},
  title = {Kozmochain: The Open Source RAG Framework},
  year = {2023},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/digitranslab/kozmochain}},
}
```
