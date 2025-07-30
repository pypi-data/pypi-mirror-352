## Question Generation Configuration

This document describes the configuration schema for the question generation process, including input data, sampling, encoding, and model settings. For more information about how to configure the LLM check: [LLM Configuration](llm_config.md)

To generate a template configuration file you can run:

```sh
benchmark_qed config init autoq local/autoq/settings.yaml
```

See more about the config init command: [Config Init CLI](config_init.md)

---

### Classes and Fields

#### `InputConfig`
Configuration for the input data used in question generation.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `dataset_path` | `Path` | _required_ | Path to the input dataset file. |
| `input_type` | `InputDataType` | `CSV` | The type of the input data (e.g., CSV, JSON). |
| `text_column` | `str` | `"text"` | The column containing the text data. |
| `metadata_columns` | `list[str] \| None` | `None` | Optional list of columns containing metadata. |
| `file_encoding` | `str` | `"utf-8"` | Encoding of the input file. |

---

#### `QuestionConfig`
Configuration for generating standard questions.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `num_questions` | `int` | `20` | Number of questions to generate per class. |
| `oversample_factor` | `float` | `2.0` | Factor to overgenerate questions before filtering. |

---

#### `ActivityQuestionConfig`
Extends `QuestionConfig` with additional fields for persona-based question generation.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `num_personas` | `int` | `5` | Number of personas to generate questions for. |
| `num_tasks_per_persona` | `int` | `5` | Number of tasks per persona. |
| `num_entities_per_task` | `int` | `10` | Number of entities per task. |

---

#### `EncodingModelConfig`
Configuration for the encoding model used to chunk documents.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `model_name` | `str` | `"o200k_base"` | Name of the encoding model. |
| `chunk_size` | `int` | `600` | Size of each text chunk. |
| `chunk_overlap` | `int` | `100` | Overlap between consecutive chunks. |

---

#### `SamplingConfig`
Configuration for sampling data from clusters.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `num_clusters` | `int` | `50` | Number of clusters to sample from. |
| `num_samples_per_cluster` | `int` | `10` | Number of samples per cluster. |
| `random_seed` | `int` | `42` | Seed for reproducibility. |

---

#### `QuestionGenerationConfig`
Top-level configuration for the entire question generation process.

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `input` | `InputConfig` | _required_ | Input data configuration. |
| `data_local` | `QuestionConfig` | `QuestionConfig()` | Local data question generation settings. |
| `data_global` | `QuestionConfig` | `QuestionConfig()` | Global data question generation settings. |
| `activity_local` | `ActivityQuestionConfig` | `ActivityQuestionConfig()` | Local activity question generation. |
| `activity_global` | `ActivityQuestionConfig` | `ActivityQuestionConfig()` | Global activity question generation. |
| `concurrent_requests` | `int` | `8` | Number of concurrent model requests. |
| `encoding` | `EncodingModelConfig` | `EncodingModelConfig()` | Encoding model configuration. |
| `sampling` | `SamplingConfig` | `SamplingConfig()` | Sampling configuration. |
| `chat_model` | `LLMConfig` | `LLMConfig()` | LLM configuration for chat. |
| `embedding_model` | `LLMConfig` | `LLMConfig()` | LLM configuration for embeddings. |

---

### YAML Example

Here is an example of how this configuration might look in a YAML file.

Save the following yaml file as autoq_settings.yaml and use with the command:

```sh
benchmark_qed autoq autoq_settings.yaml local/output_test
```

To run autoq with our AP news dataset. See the CLI Reference section for more options.

```yaml
## Input Configuration
input:
  dataset_path: datasets/AP_news/raw_data/
  input_type: json
  text_column: body_nitf
  metadata_columns: [headline, firstcreated]
  file_encoding: utf-8-sig

## Encoder configuration
encoding:
  model_name: o200k_base
  chunk_size: 600
  chunk_overlap: 100

## Sampling Configuration
sampling:
  num_clusters: 20
  num_samples_per_cluster: 10
  random_seed: 42

## LLM Configuration
chat_model:
  auth_type: api_key
  model: gpt-4.1
  api_key: ${OPENAI_API_KEY}
  llm_provider: openai.chat
embedding_model:
  auth_type: api_key
  model: text-embedding-3-large
  api_key: ${OPENAI_API_KEY}
  llm_provider: openai.embedding

## Question Generation Configuration
data_local:
  num_questions: 10
  oversample_factor: 2.0
data_global:
  num_questions: 10
  oversample_factor: 2.0
activity_local:
  num_questions: 10
  oversample_factor: 2.0
  num_personas: 5
  num_tasks_per_persona: 2
  num_entities_per_task: 5
activity_global:
  num_questions: 10
  oversample_factor: 2.0
  num_personas: 5
  num_tasks_per_persona: 2
  num_entities_per_task: 5
```

💡 Note: The api_key field uses an environment variable reference `${OPENAI_API_KEY}`. Make sure to define this variable in a .env file or your environment before running the application.

```
# .env file
OPENAI_API_KEY=your-secret-api-key-here
```

## CLI Reference

This page documents the command-line interface of the benchmark-qed autoq package.

::: mkdocs-typer2
    :module: benchmark_qed.autoq.cli
    :name: autoq
