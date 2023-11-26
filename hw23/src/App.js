import React, { useState, useEffect } from "react";
import db from "./firebase";
import { collection, getDocs, doc , getDoc, setDoc, deleteDoc} from "firebase/firestore";
import logo from "./logo.svg";

import "./modal.css";
import "./App.css";

import chat from "./openai";

import ImageComponent from "./components/ImageComponent";


const ImageModal = () => {
  return (
    <div className="modal" style={{right:"-100%"}}>
      <div className="modal-content">
        {/* card details */}
        <h1 className ="modal-heading">Card Details</h1>
        <div className="modal-box">
          <input id = "modal-card-name" type="text" placeholder="Edit Name"></input>
          <p>Last updated:&nbsp;<p id="modal-card-update">test</p> </p>
          <p>Card ID:&nbsp;<p id="modal-card-id">test</p></p>
          <p>Interactions:&nbsp;<p id="modal-card-interaction">3test</p></p>
        </div>

        
        <h2 className ="modal-heading">Conversations</h2>
        <div className="modal-box">
          <div className = "conversations-list">
            <div className="conversation">
                <div></div>
            </div>
          </div>
        </div>

        <div className="modal-buttons">
          <button className="submit-changes">submit changes</button>
          <button className = "delete-card">
            {/* delete icon */}
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
              <path stroke-linecap="round" stroke-linejoin="round" d="M14.74 9l-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 01-2.244 2.077H8.084a2.25 2.25 0 01-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 00-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 013.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 00-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 00-7.5 0" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

window.addEventListener('click', async (e) => {
  // chat('hello')
  const element = e.target;
  if (element.className === 'card') {
    const id = element.id;

    const docRef = doc(db, "people", id);
    const docSnap = await getDoc(docRef);
    const data = docSnap.data();
    console.log(data) 

    const name = data.name;
    const num_int = 1;
    const timestamp = timestamp_to_string(data.timestamp);
    // addModalInfo
    addModalInfo(name, id ,num_int, timestamp);
    openModal(element);
  }
})

window.onload = () => {
  const modal_submit = document.querySelector('.submit-changes');
  modal_submit.addEventListener('click', submit_modal_changes);

  const modal_delete = document.querySelector('.delete-card');
  modal_delete.addEventListener('click', () => {
    const modal_card_id = document.getElementById('modal-card-id');
    const id = modal_card_id.innerHTML;
    delete_card(id);
  });
}

const delete_card = (id) => {
  console.log('delete card')
  const docRef = doc(db, "people", id);
  deleteDoc(docRef).then(() => {
    console.log("Document successfully deleted!");
    const card = document.getElementById(id);
    card.remove();
  }).catch((error) => {
    console.error("Error removing document: ", error);
  });

}

const submit_modal_changes  = async () => {
  console.log('submit changes')
  const modal_card_name = document.getElementById('modal-card-name');
  const modal_card_id = document.getElementById('modal-card-id');
  const modal_card_interaction = document.getElementById('modal-card-interaction');
  const modal_card_update = document.getElementById('modal-card-update');

  const name = modal_card_name.value;
  const id = modal_card_id.innerHTML;
  const num_int = modal_card_interaction.innerHTML;
  const timestamp = modal_card_update.innerHTML;

  const docRef = doc(db, "people", id);
  const docSnap = await getDoc(docRef);
  const data = docSnap.data();
  data.name = name
  console.log(data)
  
  // set new data to firestore
  setDoc(docRef, data).then(() => {
    console.log('Document successfully written!')
    // set new data locally
    const card = document.getElementById(id);
    const card_name = card.querySelector('h4');
    card_name.innerHTML = name;
  });
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

const addModalInfo = (name = '', id = '', num_int = 0, timestamp = '', conversations = []) => {
  const modal_card_name = document.getElementById('modal-card-name');
  const modal_card_id = document.getElementById('modal-card-id');
  const modal_card_interaction = document.getElementById('modal-card-interaction');
  const modal_card_update = document.getElementById('modal-card-update');
  // const modal_conversations_list = document.querySelector('.conversations');

  modal_card_name.value = name;
  modal_card_id.innerHTML = id;
  modal_card_interaction.innerHTML = num_int;
  modal_card_update.innerHTML = timestamp;
}

function App() {
  const [people, setPeople] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getDocs(collection(db, "people"));
      setPeople(data.docs.map((doc) => ({ ...doc.data(), id: doc.id })));
      // console.log(people)
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
      <div className="search-bar"> 
        <input type="text" placeholder="Search" />
        <button className="search-button">
          {/* search icon */}
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-5.197-5.197m0 0A7.5 7.5 0 105.196 5.196a7.5 7.5 0 0010.607 10.607z" />
          </svg>

        </button>
      </div>
        <div className="grid">
          {people.map((person) => (
            <div id = {person.id} key={person.id} className="card" style={{border:'none'}}>
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
