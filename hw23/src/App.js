import React, { useState, useEffect } from "react";
import db from "./firebase";
import { collection, getDocs } from "firebase/firestore";
import { getStorage, ref, getDownloadURL } from "firebase/storage";
import logo from "./logo.svg";
import "./App.css";

function ImageComponent({ imageName }) {
  const [imageUrl, setImageUrl] = useState("");

  useEffect(() => {
    const fetchImageUrl = async () => {
      const storage = getStorage();
      const storageRef = ref(storage, "faces/" + imageName + ".jpg");

      try {
        const url = await getDownloadURL(storageRef);
        setImageUrl(url);
      } catch (error) {
        setImageUrl("/unknown.svg");
      }
    };

    fetchImageUrl();
  }, [imageName]);

  return (
    <div>
      {imageUrl && (
        <img src={imageUrl} alt="Firebase Image" width={160} height={160} />
      )}
    </div>
  );
}

function App() {
  const [people, setPeople] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      const data = await getDocs(collection(db, "people"));
      setPeople(data.docs.map((doc) => ({ ...doc.data(), id: doc.id })));
    };

    fetchData();
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <div className="grid">
          {people.map((person) => (
            <div key={person.id} className="card">
              <ImageComponent imageName={person.id} />
              <div>
                <h4>{person.name}</h4>
                <p>insert details here</p>
                <p>{person.timestamp.toDate().toString()}</p>
              </div>
            </div>
          ))}
        </div>
      </header>
    </div>
  );
}

export default App;
