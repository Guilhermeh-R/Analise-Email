from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset

# Nome do modelo base (pode trocar por outro se quiser)
model_name = "distilbert-base-uncased"

# Carregar tokenizer e modelo
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=2)

# Carregar dataset CSV
dataset = load_dataset("csv", data_files={"train": "back/train.csv"})

# Mapear labels para números
label2id = {"Produtivo": 0, "Improdutivo": 1}
id2label = {0: "Produtivo", 1: "Improdutivo"}

def encode(examples):
    inputs = tokenizer(examples["texto"], truncation=True, padding="max_length", max_length=128)
    inputs["label"] = [label2id[label] for label in examples["label"]]
    return inputs

dataset = dataset["train"].map(encode, batched=True)

# Configuração de treino
training_args = TrainingArguments(
    output_dir="./modelo_classificador",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    save_strategy="epoch",
    logging_dir="./logs",
)

# Criar trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=dataset,
)

# Treinar modelo
trainer.train()

# Salvar modelo ajustado
trainer.save_model("./modelo_classificador")
tokenizer.save_pretrained("./modelo_classificador")
