from threading import Thread
from monitor import monitor_resource_usage
from datasets import load_dataset
from transformers import GPT2Tokenizer, GPT2LMHeadModel
from transformers import DataCollatorForLanguageModeling
from transformers import Trainer, TrainingArguments

monitor_thread = Thread(target=monitor_resource_usage, args=("resource_usage.csv",))
monitor_thread.start()

# 1. 데이터셋 로딩 (IMDB 데이터셋 예시)
dataset = load_dataset("wikitext", "wikitext-103-raw-v1")

# 2. 모델 및 토크나이저 로딩
model_name = "gpt2-large"
model = GPT2LMHeadModel.from_pretrained(model_name)
tokenizer = GPT2Tokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token

# 3. 데이터 전처리 함수
def tokenize_function(examples):
    return tokenizer(examples["text"], padding="max_length", truncation=True, max_length=128)

# 4. 데이터셋 토크나이징
tokenized_dataset = dataset.map(tokenize_function, batched=True)

# 5. 데이터셋 분할 (훈련/검증)
train_test_split = tokenized_dataset["train"].train_test_split(test_size=0.1)
train_dataset = train_test_split["train"]
eval_dataset = train_test_split["test"]

# 6. 데이터 콜레이터 설정
data_collator = DataCollatorForLanguageModeling(
    tokenizer=tokenizer, mlm=False
)

# 7. 학습 인자 설정
training_args = TrainingArguments(
    output_dir="./results",
    overwrite_output_dir=True,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    per_device_eval_batch_size=4,
    evaluation_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=200,
    save_total_limit=2,
    ddp_find_unused_parameters=False
)

#monitor_thread = Thread(target=monitor_resource_usage, args=("resource_usage.csv",))
#monitor_thread.start()

# 8. 트레이너 생성
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# 9. 학습 시작
trainer.train()

# 10. 모델 저장
model.save_pretrained("./fine_tuned_gpt2")
tokenizer.save_pretrained("./fine_tuned_gpt2")

monitor_thread.join()
