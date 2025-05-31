import streamlit as st
from meme import Meme



if __name__=="__main__":
    meme = Meme()
    meme.create()
    memes = Meme.get_all()
    print(memes)