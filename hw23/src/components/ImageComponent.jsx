import React, { useState, useEffect } from "react";
import { getStorage, ref, getDownloadURL } from "firebase/storage";

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

export default ImageComponent;