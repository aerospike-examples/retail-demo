import React from "react";
import styles from "./index.module.css";

const StyleOptions = ({options}) => {
    return (
        <div className={styles.styleOptions}>
            <h4>Additional Styles</h4>
            <div className={styles.options}>
                {Object.keys(options).map(key => (
                    <a key={key} href={`/product/${key}`} className={styles.optImg}>
                        <img src={options[key].search_image} alt="Alternate Style Option" width="100%" height="auto" />
                        <span>{options[key].global_attr_base_colour}</span>
                    </a>
                ))}
            </div>
        </div>
    )
}

export default StyleOptions;