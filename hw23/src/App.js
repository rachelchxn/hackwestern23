import React, { useState, useEffect } from "react";
import db from "./firebase";
import { collection, getDocs } from "firebase/firestore";
import logo from "./logo.svg";
import "./App.css";

import ImageComponent from "./components/ImageComponent";


const ImageModal = () => {
  return (
    <div className="modal" style={{right:"-100%"}}>
      <div className="modal-content">
        <span className="close">&times;</span>
        <img src="https://via.placeholder.com/150" />
      </div>
    </div>
  );
}

const timestamp_to_string = (timestamp) => {
  const seconds = timestamp.seconds;
  const nanoSeconds = timestamp.nanoseconds;
  const date = new Date(seconds * 1000 + nanoSeconds / 1000000);
  return date.toLocaleString();
}

const openModal = (card) => {
  console.log('open modal')
  const modal = document.querySelector('.modal');
  const app_header = document.querySelector('.App-header');
  
  modal.style.right = 0;
  app_header.style.left = 0;
  app_header.style.transform = 'translateX(0%)';

  highlightCard(card)
}

const closeModal = () => {
  console.log('close modal')
  const modal = document.querySelector('.modal');
  const app_header = document.querySelector('.App-header');

  modal.style.right = '-100%'
  app_header.style.left = '50%';
  app_header.style.transform = 'translateX(-50%)';
}

const highlightCard = (card) => {
  if(card.style.border != 'none') {
    unhighlightCard(card);
    closeModal();
    return;
  }

  const cards = document.querySelectorAll('.card');
  cards.forEach(unhighlightCard);

  if(card.style.border != 'none') {
    unhighlightCard(card);
  } else {
    card.style.border = '2px solid #fff';
  }
}

const unhighlightCard = (card) => {
  card.style.border = 'none';
}

const toggleModal = () => {
  const modal = document.querySelector('.modal');
  if (modal.style.right === '0px') {
    closeModal();
  } else {
    openModal();
  }
}


window.addEventListener('click', (e) => {
  const element = e.target;
  if (element.className === 'card') {
    openModal(element);
  }
})

function App() {
  const [people, setPeople] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getDocs(collection(db, "people"));
      setPeople(data.docs.map((doc) => ({ ...doc.data(), id: doc.id })));
    };

    fetchData();
  }, []);

  // const testTime = new Date().toLocaleString();
  // left: 50%;
  // transform: translateX(-50%);
  return (
    <div className="App">
      <ImageModal/>
      <header className="App-header" style={{left:'50%', transform: 'translateX(-50%)'}}>
        <div className="grid">
          {people.map((person) => (
            <div key={person.id} className="card" style={{border:'none'}}>
              <ImageComponent imageName={person.id} />
              <div>
                <h4>{person.name}</h4>
                <p className="timestamp">Last updated: {timestamp_to_string(person.timestamp)}</p>
              </div>
            </div>
          ))}
        </div>
      </header>
    </div>
  );
}

export default App;
