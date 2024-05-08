import React from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Home from './app/home';
import Product from './app/product';
import Category from './app/category';
import App from './app';

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
                    {path: "/:product", element: <Product />, loader: () => {}},
                    {path: "/:category", element: <Category />, loader: () => {}}
                ]
            }]
        }
    ]);

    return <RouterProvider router={router} />
}

export default Routes;