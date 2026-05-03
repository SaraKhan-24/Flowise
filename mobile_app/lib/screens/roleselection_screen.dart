import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'signup_screen.dart';
import 'login_screen.dart';

class RoleSelectionScreen extends StatelessWidget {
  const RoleSelectionScreen({super.key});

  Widget _buildRoleCard(BuildContext context, String title, IconData icon, VoidCallback onSelect) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(30),
      margin: const EdgeInsets.only(bottom: 25),
      decoration: BoxDecoration(
        color: const Color(0xFFF8F9FA),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 15, offset: const Offset(0, 5)),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, size: 70, color: Colors.black),
          const SizedBox(height: 15),
          Text(
            title,
            style: GoogleFonts.poppins(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 20),
          SizedBox(
            width: 180,
            child: ElevatedButton(
              onPressed: onSelect, // <--- This now uses the function we pass in
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF007ACC),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              ),
              child: const Text("Select", style: TextStyle(color: Colors.white)),
            ),
          )
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 40),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                "Who are you?",
                style: GoogleFonts.poppins(
                  fontSize: 36,
                  fontWeight: FontWeight.bold,
                  color: const Color(0xFF2E7D8E),
                ),
              ),
              const SizedBox(height: 50),

              // 1. HOUSEHOLD CONSUMER CARD
              _buildRoleCard(
                context,
                "Household Consumer",
                Icons.home_outlined,
                    () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const SignUpScreen()),
                  );
                },
              ),

              // 2. SYSTEM ADMINISTRATOR CARD
              _buildRoleCard(
                context,
                "System Administrator",
                Icons.manage_accounts_outlined,
                    () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const LoginScreen(selectedRole: "Admin",)),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
  }