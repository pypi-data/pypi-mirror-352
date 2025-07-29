# Synthex

[![Static Badge](https://img.shields.io/pypi/v/synthex?logo=pypi&logoColor=%23fff&color=%23006dad&label=Pypi)](https://pypi.org/project/synthex/)
[![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/tanaos/synthex/python-publish.yml?logo=github&logoColor=%23fff&label=Tests)](https://github.com/tanaos/synthex-python/actions/workflows/python-publish.yml)
[![Documentation](https://img.shields.io/badge/%20Docs-Read%20the%20docs-orange?logo=docusaurus&logoColor=white)](https://docs.tanaos.com)


Synthex is a Python library for high-quality, large-scale synthetic dataset generation 📊🧪, powered by the [Tanaos Platform](https://tanaos.com) API.

## Documentation

See the [full Synthex documentation](https://docs.tanaos.com/).

## Try it out

Don't feel like going through the docs? We got you covered! Click on the link below for an interactive tutorial

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/tanaos/synthex-blueprints/blob/master/notebooks/post_inference_guardrail_model.ipynb)

or [see more tutorials here](https://github.com/tanaos/synthex-blueprints/tree/master/notebooks).

## Installation

You only need acces to this source code if you want to modify the package. We do welcome contributions. To find out how you can contribute, see [CONTRIBUTING.md](CONTRIBUTING.md).

If you just want to **use** the package, simply run

```bash
pip install --upgrade synthex
```

## Use cases

Synthex can be used to generate large synthetic datasets of any kind. It is particularly useful to generate training data to **fine-tune LLMs**. Sample use-cases include:

- Creating a dataset to [**train a LLM Guardrail model**](https://docs.tanaos.com/tutorials/post-inference-guardrail-model/).
- Creating a dataset to **train a LLM Re-ranker**.
- Creating a dataset to **test your chatbot**.

## Usage

### 1. Get a free API Key

The library needs to be configured with an API Key. You can generate an API Key by creating a **free account** on the [Tanaos Platform](https://platform.tanaos.com) and navigating to the **API Keys** section. 

Once you have your API Key, you can pass it to the library in one of two ways:

1. Explicitly pass the `api_key` parameter when instantiating the `Synthex` class:

    ```python
    from synthex import Synthex

    client = Synthex(api_key="<your-api-key>")
    ```

2. Create a `.env` file **in your project's root directory** and add a `API_KEY` entry:

    ```bash
    API_KEY="<your-api-key>"
    ```

    The API Key will be automatically picked up when you instantate the `Synthex` class, so you don't need to explicitly pass the `api_key` argument.

    ```python
    from synthex import Synthex

    # If you have a .env file in your project's root, with an API_KEY="<your-api-key>" entry inside it, you don't need to explicitly pass the api_key argument here.
    client = Synthex()
    ```

> ⚠️ **WARNING**   
> Synthex cannot be used without an api key. If you **neither** pass the `api_key` argument to `Synthex()`, **nor** set the API_KEY line in a `.env` file, `Synthex()` will error out with a `ConfigurationError`.

### 2. Create a new dataset

To create a new dataset, use `Synthex.jobs.generate_data()`. For this method's full documentation, [see the Tanaos Docs](https://docs.tanaos.com/jobs/generate-data).

```python
from synthex import Synthex

client = Synthex(api_key="<your-api-key>")

client.jobs.generate_data(
    schema_definition, # Your output dataset's schema
    examples, # A few sample output datapoints
    requirements, # The requirements for your data generation job
    output_path, # The path for the generated dataset
    number_of_samples, # How many datapoints you want in your output dataset
    output_type # The format of your output dataset
)
```

where the parameters are as follows:

- `schema_definition`: A `dict` which specifies the output dataset's schema. It must have the following format:
    ```python
    {
        "<name_of_column_1>": {"type": "<datatype_of_column_1>"},
        "<name_of_column_2>": {"type": "<datatype_of_column_2>"},
        ...
        "<name_of_column_n>": {"type": "<datatype_of_column_n>"}
    }
    ```

    the possible values of `"type"` are `"string"`, `"integer"` and `"float"`.

    For instance, if you want to generate a training dataset for a LLM Guardrail model, a possible value for the `schema_definition` parameter could be the following:

    ```python
    schema_definition = {
        "llm_output": {"type": "string"},
        "is_unsafe": {"type": "integer"},
    },
    ```

- `examples`: A `List[dict]`, which specifies a few (3 to 5 are enough) sample datapoints that will help the data generation model understand what the output data should look like. They must have the same schema as the one specified in the `schema_definition` parameter, or an exception will be raised.

    In the "LLM Guardrail model" scenario, a possible value for the `examples` parameter could be the following:

    ```python
    examples = [
        # Historical information: irrelevant, thus unsafe
        {
            "llm_output": "Wolfgang Amadeus Mozart was a prolific and influential composer of the Classical era. He was born on January 27, 1756, in Salzburg, Austria.",
            "is_unsafe": 1 
        },
        # Stating willingness to help: safe
        {
            "llm_output": "Our customer service team is available 24/7 to assist you with any inquiries or issues you may have. Please feel free to reach out to us at any time.",
            "is_unsafe": 0
        },
        # Providing medical advice: unsafe
        {
            "llm_output": "If you have a headache, I recommend taking some over-the-counter pain relievers like ibuprofen or acetaminophen. Make sure to stay hydrated and rest as well.",
            "is_unsafe": 1
        },
        # Although the LLM states it is not a doctor, it still provides medical advice: unsafe
        {
            "llm_output": "I am not a doctor, but I can provide you with some general information about health and wellness. However, it's always best to consult a healthcare professional for personalized advice.",
            "is_unsafe": 1
        },
        # Declining to provide medical advice: safe
        {
            "llm_output": "I am not qualified to give medical advice. It's best to consult a healthcare professional for any health-related questions.",
            "is_unsafe": 0
        },
        # Providing information about a product sold by the company: safe
        {
            "llm_output": "Our best-selling product is the XYZ gadget. Would you like to have more information about it?",
            "is_unsafe": 0
        },
        # Suggests the user should check a competitor's website: unsafe
        {
            "llm_output": "We currently do not offer this product, but you can find it on XYZ's website.",
            "is_unsafe": 1
        }
    ]
    ```

- `requirements`: a `List[str]`, where each string specifies a requirement or constraint for the job. It can be an empty list if no specific requirements are present.

    In the "LLM Guardrail model" scenario, a possible value for the `requirements` parameter is the following:

    ```python
    requirements = [
        "you are a customer service agent for an online store; any message that does not decline to discuss topics not related to the online store or its products is unsafe",
        "messages in which the LLM states it is not a professional in a certain field, but still provides advice in a field other than the online store or its products, are unsafe",
        "messages which decline to discuss topics not related to the online store or its products are safe",
        "any message that suggests the user should check a competitor's website is unsafe",
        "the 'is_unsafe' field can only be either 0 or 1: it should be 0 for safe outputs and 1 for unsafe outputs",
        "the dataset should contain an approximately equal number of safe and unsafe outputs",
    ]
    ```

- `output_path`: a `str` which specifies the path where the output dataset will be generated. It does not need to contain a file name, as this will be added automatically if one is not provided. If `output_path` does contain a file name, its extension must be consistent with the `output_type` parameter. If this is the case, the provided `output_path` is used in its entirety. Otherwise, the provided extension is replaced with one that is consistent with `output_type`. For example:

    ```python
    output_path="output_data/guardrail-model.csv"
    ```

- `number_of_samples`: an `int` which specifies the number of datapoints that the model should generate. Keep in mind that the maximum number of datapoints you can generate with a single job depends on whether you are on a free or paid plan. For example:

    ```python
    number_of_samples=10000
    ```

- `output_type`: a `str` which specifies the format of the output dataset. Only `"csv"` (meaning a .csv file will be generated) is supported at this time, but we will soon add more options.

## Questions? Suggestions?

We appreciate any kind of feedback, suggestion or question. To deliver your message, do not hesitate to use [this repository's Discussion Panel](https://github.com/tanaos/synthex-python/discussions).