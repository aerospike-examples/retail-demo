import React from "react";
import styles from "./index.module.css";

const Footer = () => {
    return (
        <footer className={styles.footer}>
            <span>Copyright {new Date().getFullYear()}</span>
        </footer>
    )
}

export default Footer;