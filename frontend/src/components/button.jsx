import React from 'react'
import { Link } from 'react-router-dom'

const Button = (props) => {
  return (
    <>
        <Link className= {`btn ${props.class} me-3`} to={props.url}> {props.text} </Link>
    </>
  )
}

export default Button