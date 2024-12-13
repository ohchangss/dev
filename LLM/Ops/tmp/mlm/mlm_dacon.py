from torch.utils.data import Dataset, DataLoader
import random
import torch

class BERTDataset(Dataset):
    def __init__(self, conv_pairs, tokenizer, seq_len):
        self.tokenizer = tokenizer
        self.seq_len = seq_len
        self.num_pairs = len(conv_pairs)
        self.conv_pairs = conv_pairs        # List of lists. Each item holds pair of conversation. 

    def __len__(self):
        return self.num_pairs
    
    def __getitem__(self, idx):
        # Step 1: get a random sentence pair, either negative or positive (saved as is_next_label)
        #         is_next=1 means the second sentence comes after the first one in the conversation.
        s1, s2, is_next = self.get_pair(idx)

        # Step 2: replace random words in sentence with mask / random words
        masked_numericalized_s1, s1_mask = self.mask_sentence(s1)
        masked_numericalized_s2, s2_mask = self.mask_sentence(s2)

        # Step 3: Adding CLS and SEP tokens to the start and end of sentences
        # Adding PAD token for labels
        t1 = [self.tokenizer.vocab['[CLS]']] + masked_numericalized_s1 + [self.tokenizer.vocab['[SEP]']]
        t2 = masked_numericalized_s2 + [self.tokenizer.vocab['[SEP]']]
        t1_mask = [self.tokenizer.vocab['[PAD]']] + s1_mask + [self.tokenizer.vocab['[PAD]']]
        t2_mask = s2_mask + [self.tokenizer.vocab['[PAD]']]

        # Step 4: combine sentence 1 and 2 as one input
        # adding PAD tokens to make the sentence same length as seq_len
        segment_ids = ([1 for _ in range(len(t1))] + [2 for _ in range(len(t2))])[:self.seq_len]
        bert_input = (t1 + t2)[:self.seq_len]
        bert_label = (t1_mask + t2_mask)[:self.seq_len]
        padding = [self.tokenizer.vocab['[PAD]'] for _ in range(self.seq_len - len(bert_input))]
        bert_input.extend(padding), bert_label.extend(padding), segment_ids.extend(padding)

        output = {"bert_input": bert_input,
                  "bert_label": bert_label,
                  "segment_ids": segment_ids,
                  "is_next": is_next}
        return {key: torch.tensor(value) for key, value in output.items()}

    '''
    BERT Training makes use of the following two strategies:
    1. Next Sentence Prediction (NSP)
    During training the model gets as input pairs of sentences and it learns to predict if the second sentence is the next sentence in the original text as well.
    During training the model is fed with two input sentences at a time such that:
        - 50% of the time the second sentence comes after the first one.
        - 50% of the time it is a a random sentence from the full corpus.
    BERT is then required to predict whether the second sentence is random or not, with the assumption that the random sentence will be disconnected from the first sentence:
    '''
    def get_pair(self, index):
        # conv_pairs=[["I really, really, really wanna go, but I can't. Not unless my sister goes.", "I'm workin' on it. But she doesn't seem to be goin' for him."]]
        s1, s2 = self.conv_pairs[index]
        is_next = 1
        if random.random() > 0.5:
            random_index = random.randrange(len(self.conv_pairs))
            s2 = self.conv_pairs[random_index][1]
            is_next = 0
        return s1, s2, is_next
    
    '''
    2. Masked LM (MLM): 
    Randomly mask out 15% of the words in the input — replacing them with a [MASK] token.
    Run the entire sequence through the BERT attention based encoder and then predict only the masked words, based on the context provided by the other non-masked words in the sequence. However, there is a problem with this naive masking approach — the model only tries to predict when the [MASK] token is present in the input, while we want the model to try to predict the correct tokens regardless of what token is present in the input. To deal with this issue, out of the 15% of the tokens selected for masking:
        80% of the tokens are actually replaced with the token [MASK].
        10% of the time tokens are replaced with a random token.
        10% of the time tokens are left unchanged.
    '''
    # Replace random words in sentence with mask / random words
    # s = "I really, really, really wanna go, but I can't. Not unless my sister goes."
    def mask_sentence(self, s):
        words = s.split()
        masked_numericalized_s = []
        mask = []
        for word in words:
            prob = random.random()
            token_ids = self.tokenizer(word)['input_ids'][1:-1]     # remove cls and sep token
            if prob < 0.15:                              # Mask out 15% of the words in the input
                prob /= 0.15
                for token_id in token_ids:                         # Iterate through token ids regardless of masking decision
                    if prob < 0.8:                          # Among 15%, 80% will be replaced with the token 'Mask'
                        masked_numericalized_s.append(self.tokenizer.vocab['[MASK]'])
                    elif prob < 0.9:                        # Among 15%, 10% will be replaced with a random token
                        masked_numericalized_s.append(random.randrange(len(self.tokenizer.vocab)))
                    else:                                   # Among 15%, 10% will be left unchanged
                        masked_numericalized_s.append(token_id)   # Adding unchanged tokens
                    mask.append(token_id)                          # Mask label added for each token
            else:
                masked_numericalized_s.extend(token_ids)    # Adding tokens directly if not masked
                mask.extend([0] * len(token_ids))           # Corresponding unmasked labels

        assert len(masked_numericalized_s) == len(mask)
        return masked_numericalized_s, mask