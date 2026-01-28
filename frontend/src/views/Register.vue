<template>
    <div class="register">
        <h2>Sign up</h2>
        <div class="role-tabs">
            <button @click="role = 'student'" :class="{ active: role === 'student' }">Student</button>
            <button @click="role = 'company'" :class="{ active: role === 'company' }">Company</button>
        </div>
        <form @submit.prevent="register">
            <div class="student-form" v-if="role === 'student'">
                <h3>Student Sign up</h3>
                <label class="reg-name">Name<input v-model="full_name" type="text" placeholder="Enter your full name" required /></label>
                <label class="reg-email">Email<input v-model="email" type="email" placeholder="Email" required /></label>
                <label class="reg-password">Password<input v-model="password" type="password" placeholder="Password" required /></label>
                <label class="reg-college">College<input v-model="college" type="text" placeholder="Enter your college Name" required /></label>
                <label class="reg-year">Year of Study<input v-model="year_of_study" type="number" placeholder="Enter your year of study" required /></label>
                <label class="reg-branch">Branch<input v-model="branch" type="text" placeholder="Enter your branch" required /></label>
                <label class="reg-cg">CGPA<input v-model="cgpa" type="number" step="0.01" placeholder="Enter your CGPA" required /></label>
                </div>
            <div class="company-form" v-else-if="role === 'company'">
                <h3>Company Sign up</h3>
                <label class="reg-comp">Company Name<input v-model="company_name" type="text" placeholder="Enter your Company Name" required /></label>
                <label class="reg-hr">HR Name<input v-model="hr_name" type="text" placeholder="Enter HR's Name" required /></label>
                <label class="reg-email">Email<input v-model="email" type="email" placeholder="Email" required /></label>
                <label class="reg-password">Password<input v-model="password" type="password" placeholder="Password" required /></label>
                <label class="reg-email">Website<input v-model="website" type="url" placeholder="https://example.com"  required /></label>
                <label>Description<textarea v-model="description" placeholder="Enter company description" required></textarea></label>
            </div>
            <button class="register-btn" type="submit">Register</button>    
        </form>
        <router-link class="login-link" to="/login">Already have an account? Login here.</router-link>
        <p v-if="errorMessage" style="color:red">{{ errorMessage }}</p>
    </div>
</template>
<script>
    import api from '@/services/api'
    export default{
        data(){
            return{
                role:'student',
                full_name:'',
                email:'',
                password:'',
                college:'',
                branch:'',
                year_of_study:null,
                company_name:'',
                website:'',
                description:'',
                errorMessage:'',
                cgpa:null,
                roll_number:'',
                hr_name:''
            }
        },
        methods:{
            async register(){
                try{
                    if(this.Role==='student'){
                        await api.post('/register/student',{
                            full_name:this.full_name,
                            email:this.email,
                            password:this.password,
                            college:this.college,
                            branch:this.branch,
                            year:this.year_of_study,
                            cgpa:this.cgpa
                        })
                    }else if(this.role==='company'){
                        await api.post('/register/company',{
                            company_name:this.company_name,
                            hr_name:this.hr_name,
                            email:this.email,
                            password:this.password,
                            website:this.website,
                            description:this.description,
                        })
                    }
                    this.$router.push('/login')
                }catch(error){
                    this.errorMessage='Registration failed. Please try again.'
                }
            }
        }
    }
</script>