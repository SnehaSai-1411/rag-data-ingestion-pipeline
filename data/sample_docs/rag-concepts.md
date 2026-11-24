# RAG in 30 Lines

Retrieval-augmented generation (RAG) grounds a large language model's
answers in documents you control, instead of relying only on what the
model memorised during training.

## The three steps

1. **Ingest.** Load documents, split them into chunks, embed each chunk
   into a vector, and store the vectors in a vector database. This repo
   is that step.
2. **Retrieve.** At question time, embed the question the same way and
   fetch the chunks closest to it in vector space.
3. **Generate.** Hand the question plus the retrieved chunks to the LLM
   and ask it to answer using only that context, citing its sources.

## Why chunking matters

A whole document is too long to stuff into a prompt, and a single
sentence is too thin to answer from. Chunks of a few hundred characters
strike the balance: small enough to be precise, large enough to carry
context. Paragraph-aware chunking keeps ideas whole instead of cutting
them mid-sentence, and a small overlap between neighbouring chunks
means no idea is lost at a boundary.

## Why metadata matters

Every chunk in this pipeline carries its source file and page number.
That is what lets a later answering service cite its sources — "this
claim came from rag-paper.pdf, page 4" — instead of asking the reader
to trust the model.

## What RAG does not fix

RAG cannot answer questions your documents do not cover, and it cannot
tell a true document from a false one. Retrieval quality is the ceiling
on answer quality, which is why this pipeline reports exactly what it
ingested on every run.
