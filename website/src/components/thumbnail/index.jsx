import React from "react";
import styles from "./index.module.css";
import clsx from "clsx";
import { fixImgUrl } from "../../utils";

const Thumbnail = ({img, selected, action}) => {
    let src = img?.resolutions?.["48X64"];
    return (
        src &&
        <div className={clsx(styles.thumbnailContainer, selected && styles.selected)}>
            <img 
                className={styles.thumbnail} 
                src={src ? fixImgUrl(src) : src} 
                onMouseOver={action}
                onClick={action}
            />
        </div>
    )
}

export default Thumbnail;