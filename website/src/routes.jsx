import React from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from './app/home';
import Product from './app/product';
import Category from './app/category';
import App from './app';

const url = "http://localhost:8080/rest/v1/";
             
const productLoader = async (product) => {
    let response = await fetch(url + `get?prod=${product}`);
    let data = response.json();

    return data;
}

const Routes = () => {
    const router = createBrowserRouter([
        {
            path: '/', 
            element: <App />,
            errorElement: <div />,
            children: [{
                errorElement: <div />,
                children: [
                    {index: true, element: <Home />},
                    {path: "/product/:product", element: <Product />, loader: ({params: { product}}) => productLoader(product)},
                    {path: "/category/:category", element: <Category />, loader: () => {}}
                ]
            }]
        }
    ]);

    return <RouterProvider router={router} />
}

export default Routes;