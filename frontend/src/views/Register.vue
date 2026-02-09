<template>
    <div class="auth-page">
        <div class="card register-card">
            <div class="auth-header">
                <h2>Join ProffQuest</h2>
                <p>Create your account to get started</p>
            </div>

            <div class="role-tabs">
                <button @click="role = 'student'" :class="{ active: role === 'student' }" class="role-btn">
                    <i class="fas fa-user-graduate"></i>
                    Student
                </button>
                <button @click="role = 'company'" :class="{ active: role === 'company' }" class="role-btn">
                    <i class="fas fa-building"></i>
                    Company
                </button>
            </div>

            <form @submit.prevent="register" class="register-form">
                <div class="form-section" v-if="role === 'student'">
                    <h3><i class="fas fa-user-graduate"></i> Student Registration</h3>

                    <div class="form-group">
                        <label for="full_name">
                            <i class="fas fa-user"></i>
                            Full Name
                        </label>
                        <input v-model="full_name" type="text" id="full_name" placeholder="Enter your full name" required />
                    </div>

                    <div class="form-group">
                        <label for="email">
                            <i class="fas fa-envelope"></i>
                            Email Address
                        </label>
                        <input v-model="email" type="email" id="email" placeholder="your.email@example.com" required />
                    </div>

                    <div class="form-group">
                        <label for="password">
                            <i class="fas fa-lock"></i>
                            Password
                        </label>
                        <input v-model="password" type="password" id="password" placeholder="Create a strong password" required />
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="college">
                                <i class="fas fa-university"></i>
                                College
                            </label>
                            <input v-model="college" type="text" id="college" placeholder="College name" required />
                        </div>

                        <div class="form-group">
                            <label for="year_of_study">
                                <i class="fas fa-calendar"></i>
                                Year
                            </label>
                            <input v-model="year_of_study" type="number" id="year_of_study" placeholder="1-4" min="1" max="4" required />
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="branch">
                                <i class="fas fa-code-branch"></i>
                                Branch
                            </label>
                            <input v-model="branch" type="text" id="branch" placeholder="e.g., Computer Science" required />
                        </div>

                        <div class="form-group">
                            <label for="roll_number">
                                <i class="fas fa-id-badge"></i>
                                Roll Number
                            </label>
                            <input v-model="roll_number" type="text" id="roll_number" placeholder="e.g., 21CS001" />
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="cgpa">
                                <i class="fas fa-chart-line"></i>
                                CGPA
                            </label>
                            <input v-model="cgpa" type="number" id="cgpa" step="0.01" min="0" max="10" placeholder="0.00" required />
                        </div>
                    </div>
                </div>

                <div class="form-section" v-else-if="role === 'company'">
                    <h3><i class="fas fa-building"></i> Company Registration</h3>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="company_name">
                                <i class="fas fa-building"></i>
                                Company Name
                            </label>
                            <input v-model="company_name" type="text" id="company_name" placeholder="Your company name" required />
                        </div>

                        <div class="form-group">
                            <label for="hr_name">
                                <i class="fas fa-user-tie"></i>
                                HR Name
                            </label>
                            <input v-model="hr_name" type="text" id="hr_name" placeholder="HR representative name" required />
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="email">
                            <i class="fas fa-envelope"></i>
                            Email Address
                        </label>
                        <input v-model="email" type="email" id="email" placeholder="company.email@example.com" required />
                    </div>

                    <div class="form-group">
                        <label for="password">
                            <i class="fas fa-lock"></i>
                            Password
                        </label>
                        <input v-model="password" type="password" id="password" placeholder="Create a strong password" required />
                    </div>

                    <div class="form-group">
                        <label for="website">
                            <i class="fas fa-globe"></i>
                            Website
                        </label>
                        <input v-model="website" type="url" id="website" placeholder="https://yourcompany.com" required />
                    </div>

                    <div class="form-group">
                        <label for="description">
                            <i class="fas fa-file-alt"></i>
                            Company Description
                        </label>
                        <textarea v-model="description" id="description" placeholder="Tell us about your company..." rows="4" required></textarea>
                    </div>
                </div>

                <button class="register-btn" type="submit" :disabled="isLoading">
                    <i class="fas fa-user-plus" v-if="!isLoading"></i>
                    <i class="fas fa-spinner fa-spin" v-else></i>
                    {{ isLoading ? 'Creating Account...' : 'Create Account' }}
                </button>
            </form>

            <div class="register-footer">
                <router-link class="login-link" to="/login">
                    <i class="fas fa-sign-in-alt"></i>
                    Already have an account? Sign in here
                </router-link>
            </div>

            <div v-if="errorMessage" class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                {{ errorMessage }}
            </div>
        </div>
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
                hr_name:'',
                isLoading: false
            }
        },
        methods:{
            async register(){
                this.isLoading = true;
                this.errorMessage = '';

                try{
                    if(this.role==='student'){
                        await api.post('/register/student',{
                            full_name:this.full_name,
                            email:this.email,
                            password:this.password,
                            college:this.college,
                            branch:this.branch,
                            year:this.year_of_study,
                            cgpa:this.cgpa,
                            roll_number:this.roll_number
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
                    this.errorMessage = error.response?.data?.message || 'Registration failed. Please try again.'
                } finally {
                    this.isLoading = false;
                }
            }
        }
    }
</script>
