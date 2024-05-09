import React, { useState } from "react";
import styles from "./index.module.css";
import clsx from "clsx";

const Images = ({images}) => {
    const [selected, setSelected] = useState("default");
    const { default: def, ...rest } = images;

    return (
        <div className={styles.images}>
            <div className={styles.thumbnails}>
                <img 
                    className={clsx(styles.thumbnail, selected === "default" && styles.selected)} 
                    src={def?.resolutions?.["48X64"]} 
                    onMouseOver={() => setSelected("default")} />
                {Object.keys(rest).map((key, idx) => {
                    let thumbnail = images[key]?.resolutions?.["48X64"]
                    return(
                        thumbnail &&
                        <img 
                            key={idx} 
                            className={clsx(styles.thumbnail, selected === key && styles.selected)} 
                            src={thumbnail} 
                            onMouseOver={() => setSelected(key)} />
                    )
                })}
            </div>
            <div className={styles.selectedImg}>
                <img src={images[selected].imageURL} />
            </div>
        </div>
    )
}

export default Images;