import 'package:flutter/material.dart';
import 'package:fyp/screens/user/user_dashboard.dart';
import 'package:google_fonts/google_fonts.dart';
import 'complete_uprofile_screen.dart';
import 'login1_screen.dart'; // <--- Ensure this is imported

class SignUpScreen extends StatelessWidget {
  const SignUpScreen({super.key});

  Widget _buildShadowTextField(String hint) {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(30),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: TextField(
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: GoogleFonts.poppins(color: Colors.grey, fontSize: 14),
          contentPadding: const EdgeInsets.symmetric(horizontal: 25, vertical: 15),
          border: InputBorder.none,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 30),
        child: Column(
          children: [
            const SizedBox(height: 80),
            Text(
              "Sign up to FloWise",
              style: GoogleFonts.poppins(
                fontSize: 28,
                fontWeight: FontWeight.bold,
                color: const Color(0xFF2E7D8E),
              ),
            ),

            const SizedBox(height: 40),

            // Google Sign Up Button
            SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton.icon(
                onPressed: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(builder: (context) => const CompleteProfileScreen())
                  );
                },
                icon: const Icon(Icons.g_mobiledata, size: 40, color: Colors.white),
                label: Text("Sign up with Google", style: GoogleFonts.poppins(color: Colors.white, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF007ACC),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                ),
              ),
            ),

            const SizedBox(height: 30),
            Row(children: [
              const Expanded(child: Divider()),
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 10),
                child: Text("Or continue with Email", style: GoogleFonts.poppins(fontSize: 12, fontWeight: FontWeight.w600)),
              ),
              const Expanded(child: Divider()),
            ]),

            const SizedBox(height: 20),
            _buildShadowTextField("Enter your name"),
            _buildShadowTextField("Enter username"),
            _buildShadowTextField("Enter Email"),
            _buildShadowTextField("Enter password"),

            const SizedBox(height: 40),

            // 1. Create Account Button
            SizedBox(
              width: 250,
              height: 55,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.pushAndRemoveUntil(
                    context,
                    MaterialPageRoute(builder: (context) => const UserDashboard()),
                        (route) => false,
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF007ACC),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                ),
                child: Text("Create Account", style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
              ),
            ),

            const SizedBox(height: 25), // Space between button and link

            // 2. The Login Link (Placed at the bottom of the Column)
            GestureDetector(
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => const Login1Screen()),
                );
              },
              child: RichText(
                textAlign: TextAlign.center,
                text: TextSpan(
                  style: GoogleFonts.poppins(color: Colors.black54, fontSize: 14),
                  children: [
                    const TextSpan(text: "Already have an account? "),
                    TextSpan(
                      text: "Login",
                      style: GoogleFonts.poppins(
                        color: const Color(0xFF007ACC),
                        fontWeight: FontWeight.bold,
                        decoration: TextDecoration.underline,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 40), // Final padding for scrollability
          ],
        ),
      ),
    );
  }
}