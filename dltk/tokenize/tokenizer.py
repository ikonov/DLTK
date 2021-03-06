# -*- coding: utf-8 -*-

import sys; reload(sys); sys.setdefaultencoding("utf-8")
import codecs, re, os
import cPickle as pickle
from nltk.tokenize.punkt import PunktTrainer, \
PunktSentenceTokenizer,PunktParameters
from nltk.tokenize import word_tokenize

DEUPUNCT = u""",–−—’‘‚”“‟„! £"%$'&)(+*-€/.±°´·¸;:=<?>@§#¡•[˚]»_^`≤…\«¿¨{}|"""

def txt2tmp(text):
  with codecs.open("/tmp/tmp.in","w","utf8") as tmpfile:
    print>>tmpfile, text
  return "/tmp/tmp.in"

def punct_tokenize(text):
  """ Tokenize by simply adding spaces before and after punctuations. """
  rx = re.compile('[%s]' % re.escape(DEUPUNCT), re.UNICODE)
  return [i.split() for i in rx.sub(ur" \g<0> ", text).split("\n")]

def rb_tokenize(text): # Source: http://goo.gl/sF5WA5
  """ Tokenize using a rule-base perl script by Stefanie Dipper."""
  txt2tmp(text)
  os.system("perl rbtokenize.pl -abbrev abbrev.lex /tmp/tmp.in /tmp/tmp.out")
  return [j.split() for j in \
        [i.strip() for i in codecs.open("/tmp/tmp.out","r","utf8").readlines()]]

def koehn_tokenize(text, lang='de'):
  """ Europarl v7 tokenizer tool from Philip Koehn"""
  txt2tmp(text)
  os.system("perl koehn_senttokenize.pl -l "+lang+" < /tmp/tmp.in > /tmp/tmp.out")
  os.system("perl koehn_wordtokenize.pl -l "+lang+" < /tmp/tmp.out > /tmp/tmp.in")
  return [j.split() for j in \
        [i.strip() for i in codecs.open("/tmp/tmp.in","r","utf8").readlines()]]
    
def train_punktsent(trainfile, modelfile):
  """ 
  Trains an unsupervised NLTK punkt SENTENCE tokenizer. 
  *trainfile* is the filename for the input file. s
  *modelfile* is the filename for the model output file.
  """
  punkt = PunktTrainer()
  try:
    with codecs.open(trainfile, 'r','utf8') as fin:
      punkt.train(fin.read(), finalize=False, verbose=False)
  except KeyboardInterrupt:
    print 'KeyboardInterrupt: Stopping the reading of the dump early!'
  ##HACK: Adds abbreviations from rb_tokenizer.
  abbrv_sent = " ".join([i.strip() for i in \
                         codecs.open('abbrev.lex','r','utf8').readlines()])
  abbrv_sent = "Start"+abbrv_sent+"End."
  punkt.train(abbrv_sent,finalize=False, verbose=False)
  # Finalize and outputs trained model.
  punkt.finalize_training(verbose=True)
  model = PunktSentenceTokenizer(punkt.get_params())
  with open(modelfile, mode='wb') as fout:
    pickle.dump(model, fout, protocol=pickle.HIGHEST_PROTOCOL)
  return model
   
def deupunkt_tokenize(text,modelfile=None):
  """ Modifying the unsupervised punkt algorithm in NLTK for German. """
  if modelfile == None:
    modelfile = 'deuroparl.pickle'
  try:
    with open(modelfile, mode='rb') as fin:
      sent_tokenizer = pickle.load(fin)
    # Adds DEUPUNCT from global variable. 
    sent_tokenizer.PUNCTUATION+=tuple(DEUPUNCT)
  except(IOError, pickle.UnpicklingError):
    sent_tokenizer = text.split("\n") # Backoff with "\n" as delimiter
  return [word_tokenize(i) for i in sent_tokenizer.tokenize(text)]

'''
sent = u"""„Frau Präsidentin! Ist meine Stimme mitgezählt worden?""" 
sent+=u"""Of course this a.M., it is Bros.“"""
sent = u"""Betrachten wir z.B. die Automobilindustrie, wo die Subventionen und verschiedenen staatlichen Beihilfen während des Berichtszeitraums um 24% gestiegen sind.
Zu welchem Zweck?"""

#train_punktsent('europarl-v7.de-en.de','deuroparl.pickle')
#train_punktsent('deu1000', 'deu1000.pickle')
print deupunkt_tokenize(sent, 'deu1000.pickle')
for i in deupunkt_tokenize(sent, 'deu1000.pickle'):
  print " ".join(i)
print

print koehn_tokenize(sent)
for i in koehn_tokenize(sent):
  print " ".join(i)
print

print rb_tokenize(sent)
for i in rb_tokenize(sent):
  print " ".join(i)
print

print punct_tokenize(sent)
for i in punct_tokenize(sent):
  print " ".join(i)
'''