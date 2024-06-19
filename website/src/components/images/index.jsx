import React, { useState } from "react";
import styles from "./index.module.css";
import Thumbnail from "../thumbnail";
import { fixImgUrl } from "../../utils";

const Images = ({images}) => {
    const [selected, setSelected] = useState("default");
    const { default: def, search, ...rest } = images;

    return (
        <div className={styles.images}>
            <div className={styles.thumbnails}>
                <Thumbnail img={def} selected={selected === "default"} action={() => setSelected("default")} />
                {Object.keys(rest).map((key, idx) => (
                    <Thumbnail key={idx} img={images[key]} selected={selected === key} action={() => setSelected(key)} /> 
                ))}
            </div>
            <div className={styles.selectedImg}>
                <img src={fixImgUrl(images[selected]?.resolutions["360X480"])} />
            </div>
        </div>
    )
}

export default Images;