import React, { useEffect, useRef, useState } from "react";
import styles from "./index.module.css";
import clsx from "clsx";
import { Chevron } from "../../components/icons";

const ProductDetail = ({name, descriptors}) => {
    const [open, setOpen] = useState(false);
    const [height, setHeight] = useState(450);
    const [elemHeight, setElemHeight] = useState(0);

    const toggleOpen = () => {
        setOpen(!open);
        setHeight(open ? 450 : elemHeight + 32);
    }

    const descriptionRef = useRef(null);
    useEffect(() => {
        setElemHeight(descriptionRef?.current?.clientHeight)
    }, [])

    const formatHTML = (value, prepend = null) => {
        if(value) {
            if(value === "<p>NA</p>") return null;
            value = value
                .replaceAll("<a", "<span")
                .replaceAll("</a>", "</span>")
                .replaceAll("<strong><br /></strong>", "")
                .replace("<br /><br /></span>", "</span>")
                .replace("<br /><br /></p>", "</p>");
            value = prepend ? value.replace(prepend[0], prepend[1]) : value;
        }
        return value
    }
    
    let description = formatHTML(descriptors?.description?.value);
    let style_note = formatHTML(descriptors?.style_note?.value);
    let size_fit_desc = formatHTML(descriptors?.size_fit_desc?.value, ["<p>", "<p><strong>Fit<br /></strong>"]);
    let materials_care_desc = formatHTML(descriptors?.materials_care_desc?.value, ["<p>", "<p><strong>Wash care<br /></strong>"]);

    return (
        <div className={styles.prodDetail}>
            <h2>{name}</h2>
            <div className={styles.descContainer} style={{height: `${height}px`}}>

                <div 
                    className={styles.description} 
                    dangerouslySetInnerHTML={{__html: description + (style_note ? style_note : "") + (size_fit_desc ? size_fit_desc : "") + (materials_care_desc ? materials_care_desc : "")}}
                    ref={descriptionRef} />
            </div>
            {elemHeight > 450 &&
            <div className={styles.more} onClick={toggleOpen}>
                <Chevron className={clsx(styles.chevron, open && styles.open)} />
            </div>}
        </div>
    )
}

export default ProductDetail;