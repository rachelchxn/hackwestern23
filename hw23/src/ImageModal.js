import React from "react";
import { doc, deleteDoc, setDoc, getDoc } from "firebase/firestore";
import db from "./firebase"; // Adjust the import path as needed

const ImageModal = ({ isOpen, onClose, cardDetails, refreshData }) => {
  const { id, numInteractions, lastUpdated } = cardDetails || {};

  const handleCloseClick = () => {
    if (onClose) {
      onClose();
    }
  };
  const [name, setName] = React.useState(cardDetails.name);
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleDelete = async () => {
    try {
      const docRef = doc(db, "people", cardDetails.id);
      await deleteDoc(docRef);
      console.log("Document successfully deleted!");
      refreshData(); // Call a function passed from parent to refresh data
      onClose(); // Close modal
    } catch (error) {
      console.error("Error removing document: ", error);
    }
  };

  const handleSubmitChanges = async () => {
    setIsSubmitting(true);
    try {
      const docRef = doc(db, "people", cardDetails.id);
      const updatedData = { ...cardDetails, name };
      await setDoc(docRef, updatedData);
      console.log("Document successfully written!");
      refreshData(); // Refresh data in parent component
      onClose(); // Close modal
    } catch (error) {
      console.error("Error updating document: ", error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className={`modal ${isOpen ? "modal-open" : "modal-hidden"}`}>
      <div className="modal-content">
        <h1 className="modal-heading">Card Details</h1>
        <div className="modal-box">
          <input
            id="modal-card-name"
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <p>
            Last updated:&nbsp;<span id="modal-card-update">{lastUpdated}</span>
          </p>
          <p>
            Card ID:&nbsp;<span id="modal-card-id">{id}</span>
          </p>
          <p>
            Interactions:&nbsp;
            <span id="modal-card-interaction">{numInteractions}</span>
          </p>
        </div>

        <h2 className="modal-heading">Conversations</h2>
        <div className="modal-box">
          <div className="conversations-list">
            {/* Conversations will be listed here */}
          </div>
        </div>

        <div className="modal-buttons">
          <button onClick={handleSubmitChanges} disabled={isSubmitting}>
            Submit Changes
          </button>
          <button onClick={handleDelete}>Delete</button>
          <button className="delete-card" onClick={handleCloseClick}>
            {/* Delete icon or text */}
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ImageModal;
