import React, { useState } from "react";
import styles from "./index.module.css";
import clsx from "clsx";

const SizeOptions = ({options}) => {
    const [selected, setSelected] = useState(0);

    return (
        <div className={styles.options}>
            <h4>Size</h4>
            <div className={styles.sizeOptions}>
                {options.map((option, idx) => (
                    <div 
                        key={idx} 
                        className={clsx(styles.option, selected === idx && styles.selected)}
                        onClick={() => setSelected(idx)}>
                        <span>{option.value}</span>
                    </div>
                ))}
            </div>
        </div>
    )
}

export default SizeOptions;