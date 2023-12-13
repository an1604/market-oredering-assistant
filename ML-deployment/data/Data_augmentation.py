import nlpaug.augmenter.word as naw
import pandas as pd
import nltk

nltk.download('wordnet')

buy = ['I want to buy some chicken', 'add cheese to my cart', 'add this to my cart', 'add ',
       'I want to buy chocolate']
remove = ['I want to remove from my cart', 'remove from my cart', 'remove the last product from my cart',
          'remove the white cheese from my cart', 'remove this from my cart', 'remove']
finish = ['I want to finish my order', 'Cancel my order', 'I am done for now', 'I want to pay',
          'finish my order', 'Cancel my order']

data = {
    'text': buy + remove + finish,
    'label': [0] * len(buy) + [1] * len(remove) + [2] * len(finish)
}

df = pd.DataFrame(data)

num_augmented_samples = 500
augmenter = naw.SynonymAug(aug_src='wordnet')

sample = data['text'][0]
print('Original Text:', sample)
print('Augmented Text:', augmenter.augment(sample))

augmented_texts = [augmenter.augment(text) for _ in range(num_augmented_samples) for text in df['text']]
augmented_labels = [label for _ in range(num_augmented_samples) for label in df['label']]

augmented_df = pd.DataFrame({
    'text': augmented_texts,
    'label': augmented_labels
})

combined_df = pd.concat([df, augmented_df], ignore_index=True)
combined_df.to_csv('buy_remove_finish_data.csv', index=False)
