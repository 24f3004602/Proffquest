<template>
  <div class="login">
    <h3>Sign in</h3>
    <form @submit.prevent="login">
        <div>
    <label>Email</label>
    <input v-model="email" type="email" placeholder="Email" required  />
    </div>
    <div>
      <label>Password</label>
      <input v-model="password" type="password" placeholder="Password" required /> 
      </div> 
        <button type="submit">Login</button>
    </form>
  <p v-if="errorMessage" style="color:red">{{ errorMessage }}</p>
    <router-link class="register-link" to="/register">Don't have an account? Register here.</router-link>
        
</div>
    
    </template>


<script>
    import api from '@/services/api'
    export default{
        data(){
            return{
                email:'',   
                password:'',
                errorMessage:''
            }
        },
        methods:{
            async login(){
                try{
                    const response=await api.post('/login',{ //sending data to api created in backend with route /login because in services/api.js 
                    // we have set the base url to http://localhost:5000/api
                        email:this.email,
                        password:this.password
                    })
                    const access_token=response.data.access_token
                    localStorage.setItem('access_token',access_token)
                    const payload=JSON.parse(atob(access_token.split('.')[1]))
                    const role=payload.sub.role
                    localStorage.setItem('role', role)//storing role in local storage to identify user role
                    if(role==='admin'){
                        this.$router.push('/admin/dashboard')
                    }else if(role==='Student'){
                        console.log("student logged in")
                        this.$router.push('/student/dashboard')
                    }else if(role==='company'){
                        this.$router.push('/company/dashboard')
                    }
                }catch(error){
                    this.errorMessage='Invalid email or password'
                }
            }
        }
    }
</script>