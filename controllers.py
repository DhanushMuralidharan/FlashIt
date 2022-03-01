from flask import render_template,request,redirect,url_for,session
from config import app,db
import random
from models import user,deck,card
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@app.route('/')
def Index():
  return render_template('Index.html')

@app.route('/signin',methods=['GET','POST'])
def Signin():
  if 'user' not in session.keys() or session['user'] is None:
    if request.method == 'GET':
      return render_template('signin.html')
    elif request.method == 'POST':
      uname = request.form.get('username')
      pw = request.form.get('password')
      User = user.query.filter(user.user_name == uname).one()
    
      if User.verify_password(pw):
        print('Successfully signed in!')
        session['user'] = User.user_id
        return redirect(url_for('Decks'))
      else:
        print('Password mismatch!')
        return redirect(url_for('Signin'))
  else:
    return redirect(url_for('Decks'))
    

@app.route('/signup',methods=['GET','POST'])
def Signup():
  if 'user' not in session.keys() or session['user'] is None:
    if request.method == 'GET':
      return render_template('signup.html')
    elif request.method == 'POST':
      uname=request.form.get('username')
      disp_name=request.form.get('display_name')
      password=request.form.get('password')
      object=user(uname,disp_name,password)
      db.session.add(object)
      db.session.commit()
      userid = (user.query.filter(user.user_name==uname).one())
      session['user']=userid.user_id
      return redirect(url_for('Decks'))
  else:
    return redirect(url_for('Decks'))


@app.route('/logout')
def logout():
  session['user'] = None
  return redirect(url_for('Index'))

@app.route('/decks')
def Decks():
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  elif session['user'] is not None:
    User = user.query.filter(user.user_id == session['user']).one()
    return render_template('Decks.html',USER = User)


@app.route('/decks/new',methods =['POST','GET'])
def newDeck():
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  elif session['user'] is not None:
    if request.method == 'GET':
      return render_template('newDeck.html')
    elif request.method =='POST':
      deck_name=request.form.get('deck_name')
      owner=session['user']
      object=deck(deck_name,owner)
      db.session.add(object)
      db.session.commit()
      return redirect(url_for('Decks'))
 

@app.route('/decks/<int:deck_id>/delete')
def deleteDeck(deck_id):
  d = deck.query.filter(deck.deck_id == deck_id).one()
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  elif int(d.owner) == session['user']:
    for c in d.cards:
      db.session.delete(c)
      db.session.commit()
    db.session.delete(d)
    db.session.commit()
    return redirect(url_for('Decks'))
  else:
    return redirect(url_for('Decks'))


@app.route('/decks/<int:deck_id>/<int:card_id>/delete')
def deleteCard(deck_id,card_id):
  d = deck.query.filter(deck.deck_id == deck_id).one()
  c = card.query.filter(card.card_id == card_id).one()
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  elif int(d.owner) == session['user']:
    db.session.delete(c)
    db.session.commit()
    return redirect(url_for('viewDeck',deck_id=deck_id))
  else:
    return redirect(url_for('Decks'))

@app.route('/decks/<int:deck_id>/<int:card_id>/update',methods = ['POST','GET'])
def updateCard(deck_id,card_id):
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  if request.method == 'GET':
    c = card.query.filter(card.card_id == card_id).one()
    return render_template('updatecard.html',c=c)
  elif request.method == 'POST':
    c = card.query.filter(card.card_id == card_id).one()
    c.key = request.form.get('key')
    c.answer=request.form.get('answer')
    c.difficulty=request.form.get('difficulty')
    db.session.commit()
    return redirect(url_for('viewDeck',deck_id=deck_id))


@app.route('/decks/<int:deck_id>')
def viewDeck(deck_id):
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  if request.method == 'GET':
    Deck = deck.query.filter(deck.deck_id == deck_id).one()
    if (int(Deck.owner) == session['user']):
      return render_template('viewDeck.html',DECK=Deck)
    elif session['user'] is None:
      return redirect(url_for('Index'))
    else:
      print('Invalid access!')
      return redirect(url_for('Decks'))

@app.route('/decks/<int:deck_id>/<int:card_id>')
def viewCard(deck_id,card_id):
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  Deck = deck.query.filter(deck.deck_id == deck_id).one()
  if (int(Deck.owner) == session['user']):
    if request.method == 'GET':
      Card = card.query.filter(card.card_id == card_id).one()     
      return render_template('viewCard.html',DECK=Deck,CARD=Card)
  else:
    print('Invalid access!')
    return redirect(url_for('Decks'))
    





@app.route('/decks/<int:deck_id>/newCard',methods =['POST','GET'])
def newCard(deck_id):
    if 'user' not in session.keys() or session['user'] is None:
      return redirect(url_for('Index'))
    Deck = deck.query.filter(deck.deck_id == deck_id).one()
    if (int(Deck.owner) == session['user']):
      if request.method == 'GET':
        return render_template('newCard.html',DECK=Deck) 
      elif request.method == 'POST':
        KEY=request.form.get('key')
        ANSWER=request.form.get('answer')
        DIFFICULTY=request.form.get('difficulty')
        object = card(deck_id,KEY,ANSWER,DIFFICULTY)
        db.session.add(object)
        db.session.commit()
        return redirect(url_for('viewDeck',deck_id=deck_id))
    else:
      print('Invalid access!')
      return redirect(url_for('Decks'))

@app.route('/decks/<int:deck_id>/play',methods=['POST','GET'])
def Play(deck_id):
  if 'user' not in session.keys() or session['user'] is None:
    return redirect(url_for('Index'))
  print(request.method)
  if request.method=='POST':
    Deck = deck.query.filter(deck.deck_id == deck_id).one()
    count = int(request.form.get('count'))
    diff = request.form.getlist('difficulty')
    if diff == []:
      diff = ['easy','medium','hard']
    cards = card.query.filter(card.deck_id == deck_id)
    display_cards = []
    for c in cards:
      if c.difficulty in diff:
        display_cards.append(c)
    count = min(count,len(display_cards))
    display_cards = random.sample(display_cards,count)
    return render_template('Play.html',cards=display_cards,DECK=Deck)
