from trankit import TPipeline

trainer = TPipeline(training_config={
    'task': 'posdep',
    'category':'customized',
    'save_dir': './trankit/saved_model',
    #'train_txt_fpath': './trankit/train.txt',
    'train_conllu_fpath': './trankit/he_htb-ud-train.conllu',
    #'dev_txt_fpath': './trankit/dev.txt',
    'dev_conllu_fpath': './trankit/he_htb-ud-dev.conllu'
    }
)

trainer.train()