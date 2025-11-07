import React from 'react'
import Button from './button.jsx'


const Main = () => {
  return (
    <>
      <div className='container'>
        <div className='p-5 text-center  bg-light-dark rounded'>
            
            <h1 className='text-light'>VDE Attendance Portal</h1>
            <p className='text-light' lead >Welcome to VDE Attendance Portal.</p>
            <Button text="Explore Now" class="btn-outline-info" url='/attendance'/>
        </div>
      </div>
      
    </>
  )
}

export default Main