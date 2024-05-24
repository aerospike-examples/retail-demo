import React from "react";
import styles from "./index.module.css";

const Footer = () => {
    return (
        <footer className={styles.footer}>
            <div className={styles.content}>
                <span>All trademarks, logos, and brand names are the property of their respective owners.</span>
                <span>The use of this website and its content are intended for educational purposes only. AeroApparel is a fictitous brand and no association with any real company, organization, product, domain name, e-mail address, logo, person, places, or events is intended or should be inferred.</span>
                <div className={styles.attribution}>
                    <span>Product Data and Images provided by:</span>
                    <a href="https://www.kaggle.com/datasets/paramaggarwal/fashion-product-images-dataset" rel="noopener noreferrer" target="_blank">Kaggle - Fashion Product Images Dataset</a>
                </div>
            </div>
        </footer>
    )
}

export default Footer;