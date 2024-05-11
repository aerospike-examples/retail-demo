import React from "react";
import styles from "./index.module.css";

const NotFound = () => {
    return (
        <div className={styles.notFound}>
            <img src="https://64.media.tumblr.com/tumblr_lz2ufhclZj1r4mh0bo1_r1_400.gifv" />
            <h1>Oops...</h1>
            <p>looks like that page doesn't exist</p>
        </div>
    )
}

export default NotFound;