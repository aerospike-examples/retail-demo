import React from "react";
import styles from "./index.module.css";

const Footer = () => {
    return (
        <footer className={styles.footer}>
            <span>&#169; {new Date().getFullYear()} AeroApparel</span>
        </footer>
    )
}

export default Footer;