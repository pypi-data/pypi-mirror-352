from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load the model and tokenizer
model_name = "facebook/nllb-200-distilled-600M"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Example: Translate from English to Swahili
input_text = "Hello, how are you?"
src_lang = "eng_Latn"
tgt_lang = "swh_Latn"

# Tokenize input
tokenizer.src_lang = src_lang
encoded = tokenizer(input_text, return_tensors="pt")

# Generate and decode
generated_tokens = model.generate(**encoded, forced_bos_token_id=tokenizer.lang_code_to_id[tgt_lang])
output_text = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]

print(output_text)