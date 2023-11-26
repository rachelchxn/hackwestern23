// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";

// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBpsfkfeiIj6lJAfZPI8romlWcNJrPtnBg",
  authDomain: "hw23-e0512.firebaseapp.com",
  projectId: "hw23-e0512",
  storageBucket: "hw23-e0512.appspot.com",
  messagingSenderId: "592135931369",
  appId: "1:592135931369:web:fc6ee1e83921105360b778",
  measurementId: "G-LYV8H0KGB6",
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app);

export default db;
