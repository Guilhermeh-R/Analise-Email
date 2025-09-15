from transformers import GPT2LMHeadModel, GPT2Tokenizer, Trainer, TrainingArguments, TextDataset, DataCollatorForLanguageModeling

# --- Modelo base ---
model_name = "gpt2"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)

# GPT-2 não tem token de padding, então usamos eos_token
tokenizer.pad_token = tokenizer.eos_token

# --- Carregar dataset ---
def load_dataset(file_path, tokenizer, block_size=128):
    return TextDataset(
        tokenizer=tokenizer,
        file_path=file_path,
        block_size=block_size
    )

train_dataset = load_dataset("back/email-dataset.txt", tokenizer)

# --- Data collator ---
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer,
    mlm=False
)

# --- Configurações de treino ---
training_args = TrainingArguments(
    output_dir="./modelo_geracao",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    save_steps=500,
    save_total_limit=2,
    logging_dir="./logs",
    logging_steps=100,
)

# --- Trainer ---
trainer = Trainer(
    model=model,
    args=training_args,
    data_collator=data_collator,
    train_dataset=train_dataset,
)

# --- Treinar ---
trainer.train()

# --- Salvar modelo treinado ---
model.save_pretrained("./modelo_geracao")
tokenizer.save_pretrained("./modelo_geracao")
print("Treinamento finalizado e modelo salvo em ./modelo_geracao")
