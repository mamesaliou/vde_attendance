import React from 'react'
import { useState } from 'react'
//import axios from 'axios'
import ance from '../axiosInstance.js'
import { ENDPOINTS } from '../api/endpoints.js'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
import { faSpinner } from '@fortawesome/free-solid-svg-icons'

const Register = () => {
    const [first_name, setFirst_name] = useState('')
    const [last_name, setLast_name] = useState('')
    const [role, setRole] = useState('')
    const [class_id, setClass_id] = useState('')

    const [username, setUsername] = useState('')
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('')
    const [errors, setErrors]= useState({})
    const [success, setSuccess]= useState(false)
    const [loading, setLoading] = useState(false)

    const  handleRegistration = async (e)=>{
        e.preventDefault();
        setLoading(true);
    const userData ={
        username, email, password, first_name, last_name, role, class_id
    }
    console.log("userdata: ", userData)
    try{
        const response = await ance.post(ENDPOINTS.REGISTER, userData)// await axios.post('http://127.0.0.1:8000/api/auth/register/', userData)
        console.log("response.data ==>", response.data)
        console.log("registration successful")
        setErrors({})
        setSuccess(true)

    }catch (error) {
        setErrors(error.response.data)
        console.error("registration error: ", error.response.data)

    }finally{
        setLoading(false)
    }
    }
        

  return (
<>
    <div className= 'container' >
        <div className='row justify-content-center'>
            <div className="col-md-6 bg">
                <h3 className="text-light text-center p-5 rounded mb-4" >
                    Create an Account
                </h3>
                <form onSubmit={handleRegistration}>
                    
                    <div className='mb-3'>
                        <input type="text" className='form-control'  placeholder='Username' value={username} onChange={(e)=> setUsername(e.target.value)}/>
                        <small>{errors.username && <div className='text-danger'>{errors.username} </div>} </small>
                    </div>
                    
                    <div className="mb-3">
                        <input type="email" className='form-control' placeholder='Email address' value={email} onChange={(e)=>setEmail(e.target.value)}/> 
                        <small>{errors.email && <div className='text-danger'>{errors.email} </div>} </small>
                    </div>
                    
                    <div className="mb-3">
                        <input type="password" className='form-control' placeholder='Set password' value={password} onChange={(e)=>setPassword(e.target.value)}/> 
                        <small>{errors.password && <div className='text-danger'>{errors.password}</div>} </small>
                    </div>

                    <div className="mb-3">
                        <input type="first_name" className='form-control' placeholder='Set first_name' value={first_name} onChange={(e)=>setFirst_name(e.target.value)}/> 
                        <small>{errors.first_name && <div className='text-danger'>{errors.first_name}</div>} </small>
                    </div>

                     <div className="mb-3">
                        <input type="last_name" className='form-control' placeholder='Set last_name' value={last_name} onChange={(e)=>setLast_name(e.target.value)}/> 
                        <small>{errors.last_name && <div className='text-danger'>{errors.last_name}</div>} </small>
                    </div>

                     <div className="mb-3">
                        <input type="role" className='form-control' placeholder='Set role' value={role} onChange={(e)=>setRole(e.target.value)}/> 
                        <small>{errors.role && <div className='text-danger'>{errors.role}</div>} </small>
                    </div>

                    <div className="mb-3">
                        <input type="class_id" className='form-control' placeholder='Set class_id' value={class_id} onChange={(e)=>setClass_id(e.target.value)}/> 
                        <small>{errors.class_id && <div className='text-danger'>{errors.class_id}</div>} </small>
                    </div>


                    {success && <div className='alert alert-success'> Registration Successeful</div>}
                    {loading ? (
                        <button type='submit' className='btn btn-info d-block mx-auto' disable> <FontAwesomeIcon icon={faSpinner} spin/> Please wait... </button>
                    ): (
                     <button type='submit' className='btn btn-info d-block mx-auto'>Register</button>
  
                    )}
            
                </form>

            </div>

        </div>

    </div>
</>
  )
}

export default Register