

import os
import json
# from flask import Flask, render_template, request, jsonify
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from main import DRIForesightProcessor, initialize_processor
# from policy_stress_test import create_stress_test_processor
# from google.cloud import translate_v3
import os

from deep_translator import GoogleTranslator

load_dotenv()
# processor = None

def create_app() -> Flask:
    app = Flask(__name__, template_folder="Templates")
    app.secret_key = 'dri-foresight-wind-tunnel-2024'

    # Initialize processor once per app lifecycle (stateless per request payload)
    try:
        processor = initialize_processor()
    except Exception as exc:
        processor = None
        app.logger.error(f"Failed to initialize DRIForesightProcessor: {exc}")

    class FlaskFileWrapper:
        """Adapter to make Werkzeug's FileStorage look like our expected file object."""
 
        def __init__(self, file_storage):
            self._file = file_storage
            self.name = file_storage.filename
 
        def read(self, *args, **kwargs):
            return self._file.read(*args, **kwargs)
 
        def seek(self, *args, **kwargs):
            # FileStorage exposes underlying stream with seek
            return self._file.stream.seek(*args, **kwargs)
       
        def tell(self, *args, **kwargs):
            return self._file.tell(*args, **kwargs)
       
        def seekable(self, *args, **kwargs):
            return self._file.seekable(*args, **kwargs)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health", methods=["GET"])
    def health():
        ok = processor is not None and bool(os.getenv("GROQ_API_KEY"))
        return jsonify({"ok": ok})

    @app.route("/api/generate-domain-map", methods=["POST"])
    def generate_domain_map():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        project_name = request.form.get("project_name", "").strip()
        final_domain = request.form.get("final_domain", "").strip()

        if not project_name or not final_domain:
            return jsonify({"error": "Missing project_name or final_domain"}), 400

        # Collect uploaded documents (stateless: only for this call)
        documents = request.files.getlist("documents")

        all_text = ""
        for f in documents:
            try:
                wrapper = FlaskFileWrapper(f)
                wrapper.seek(0)
                extracted = processor.extract_text_from_file(wrapper)
                all_text += (extracted or "") + "\n\n"
            except Exception as exc:
                all_text += f"Could not extract text from {f.filename}: {exc}\n\n"

        result = processor.generate_domain_map(final_domain, all_text, project_name)
        return jsonify({"domain_map": result})
    
    @app.route("/api/generate-mindmap", methods=["POST"])
    def generate_mindmap():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        try:
            domain_map_json = request.form.get("domain_map", "{}")
            domain = request.form.get("domain", "")
            
            domain_map_data = json.loads(domain_map_json)
            
            # For now, return the domain map data formatted for mind map
            # You can enhance this with AI processing if needed
            
            result = {
                "central_domain": domain_map_data.get("central_domain", domain),
                "sub_domains": domain_map_data.get("sub_domains", [])
            }
            
            return jsonify({"mindmap_data": result})
            
        except Exception as e:
            return jsonify({"error": f"Failed to generate mind map: {str(e)}"}), 500

    @app.route("/api/analyze-interviews", methods=["POST"])
    def analyze_interviews():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        domain = request.form.get("domain", "").strip()
        if not domain:
            return jsonify({"error": "Missing domain"}), 400

        interviews = request.files.getlist("interviews")
        full_interview_text = ""
        for f in interviews:
            wrapper = FlaskFileWrapper(f)
            wrapper.seek(0)
            try:
                text = processor.extract_text_from_file(wrapper)
            except Exception as exc:
                text = f"Could not read {f.filename}: {exc}"
            full_interview_text += f"\n\n--- INTERVIEW FILE: {f.filename} ---\n" + (text or "") + "\n\n"

        analysis = processor.analyze_interview_data(domain, full_interview_text)
        return jsonify({
            "interview_analysis": analysis,
            "full_interview_text": full_interview_text,
        })

    @app.route("/api/generate-signals", methods=["POST"])
    def generate_signals():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        domain = request.form.get("domain", "").strip()
        if not domain:
            return jsonify({"error": "Missing domain"}), 400

        # UPDATED: Collect all file types using the new comprehensive approach
        files_dict = {
            'documents': request.files.getlist("documents"),
            'signals': request.files.getlist("signals"), 
            'interviews': request.files.getlist("interviews"),
            'domain_map': request.files.get("domain_map")  # Single file
        }
        
        # Convert to FlaskFileWrapper format
        wrapped_files = {}
        for file_type, file_list in files_dict.items():
            if file_type == 'domain_map' and file_list:
                wrapped_files[file_type] = FlaskFileWrapper(file_list)
            elif file_list:
                wrapped_files[file_type] = [FlaskFileWrapper(f) for f in file_list]
        
        # USE: New comprehensive text extraction method
        all_text = processor.extract_comprehensive_text(wrapped_files)
        
        signals_data = processor.generate_signals(domain, all_text)
        return jsonify({"signals_data": signals_data})

    @app.route("/api/generate-ai-suggestions", methods=["POST"])
    def generate_ai_suggestions():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        payload = request.get_json(silent=True) or {}
        domain = payload.get("domain", "").strip()
        signals_data = payload.get("signals_data", {})

        if not domain:
            return jsonify({"error": "Missing domain"}), 400

        suggestions = processor.generate_ai_suggestions(domain, signals_data or {})
        return jsonify({"suggestions": suggestions})

    @app.route("/api/generate-steepv", methods=["POST"])
    def generate_steepv():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        domain = request.form.get("domain", "").strip()
        if not domain:
            return jsonify({"error": "Missing domain"}), 400

        try:
            import json as _json
            signals_data = _json.loads(request.form.get("signals_data", "{}"))
        except Exception:
            signals_data = {}

        # UPDATED: Use comprehensive file collection approach
        files_dict = {
            'documents': request.files.getlist("documents"),
            'signals': request.files.getlist("signals"), 
            'interviews': request.files.getlist("interviews"),
            'domain_map': request.files.get("domain_map")
        }
        
        # Convert to FlaskFileWrapper format
        wrapped_files = {}
        for file_type, file_list in files_dict.items():
            if file_type == 'domain_map' and file_list:
                wrapped_files[file_type] = FlaskFileWrapper(file_list)
            elif file_list:
                wrapped_files[file_type] = [FlaskFileWrapper(f) for f in file_list]
        
        # USE: New comprehensive text extraction method
        all_text = processor.extract_comprehensive_text(wrapped_files)

        steepv = processor.generate_steepv_analysis(domain, signals_data or {}, all_text)
        return jsonify({"steepv": steepv})

    @app.route("/api/generate-futures-triangle", methods=["POST"])
    def generate_futures_triangle():
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        # UPDATED: Handle FormData instead of JSON payload
        try:
            import json as _json
            request_data = _json.loads(request.form.get("request_data", "{}"))
            domain = request_data.get("domain", "").strip()
            signals_data = request_data.get("signals_data", {})
            steepv_data = request_data.get("steepv_data", {})
            document_context = request_data.get("document_context", {})
        except Exception:
            return jsonify({"error": "Invalid request data format"}), 400

        if not domain:
            return jsonify({"error": "Missing domain"}), 400

        # UPDATED: Collect all file types for comprehensive analysis
        files_dict = {
            'documents': request.files.getlist("documents"),
            'signals': request.files.getlist("signals"), 
            'interviews': request.files.getlist("interviews"),
            'domain_map': request.files.get("domain_map")
        }
        
        # Convert to FlaskFileWrapper format
        wrapped_files = {}
        for file_type, file_list in files_dict.items():
            if file_type == 'domain_map' and file_list:
                wrapped_files[file_type] = FlaskFileWrapper(file_list)
            elif file_list:
                wrapped_files[file_type] = [FlaskFileWrapper(f) for f in file_list]
        
        # USE: Comprehensive text extraction for full context
        interview_context = processor.extract_comprehensive_text(wrapped_files)

        triangle = processor.generate_futures_triangle(domain, signals_data or {}, steepv_data or {}, interview_context or "")
        return jsonify({"futures_triangle": triangle})
    
    # ADD: New Flask routes for saving edited content

    @app.route("/api/save-steepv", methods=["POST"])
    def save_steepv():
        """Save edited STEEPV analysis"""
        try:
            payload = request.get_json(silent=True) or {}
            domain = payload.get("domain", "").strip()
            steepv_data = payload.get("steepv_data", {})
            
            if not domain:
                return jsonify({"error": "Missing domain"}), 400
            
            # Here you can save to database/file if needed
            # For now, just return success
            return jsonify({
                "success": True, 
                "message": "STEEPV analysis saved successfully",
                "saved_data": steepv_data
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/api/save-futures-triangle", methods=["POST"])
    def save_futures_triangle():
        """Save edited Futures Triangle analysis"""
        try:
            payload = request.get_json(silent=True) or {}
            domain = payload.get("domain", "").strip()
            futures_triangle_data = payload.get("futures_triangle_data", {})
            
            if not domain:
                return jsonify({"error": "Missing domain"}), 400
            
            # Here you can save to database/file if needed
            # For now, just return success
            return jsonify({
                "success": True, 
                "message": "Futures Triangle saved successfully",
                "saved_data": futures_triangle_data
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # ADD: New Flask route for saving Phase 1 progress

    @app.route("/api/save-phase1-progress", methods=["POST"])
    def save_phase1_progress():
        """Save Phase 1 progress data"""
        try:
            payload = request.get_json(silent=True) or {}
            
            # Extract data
            project_name = payload.get("project_name", "")
            final_domain = payload.get("final_domain", "")
            
            if not project_name:
                return jsonify({"error": "Project name is required"}), 400
            
            # Here you can save to database/file if needed
            # For now, just validate and return success
            
            return jsonify({
                "success": True,
                "message": "Phase 1 progress saved successfully",
                "saved_data": {
                    "project_name": project_name,
                    "domain": final_domain,
                    "timestamp": payload.get("timestamp"),
                    "has_domain_map": payload.get("domain_map_generated", False),
                    "has_interview_analysis": payload.get("interview_analysis_generated", False)
                }
            })
            
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/generate-futures-triangle-2-0', methods=['POST'])
    def generate_futures_triangle_2_0():
        try:
            # Get form data and files
            domain = request.form.get('domain', '').strip()
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            # Get Phase 1 & 2 saved data
            phase1_data = json.loads(request.form.get('phase1_data', '{}'))
            phase2_data = json.loads(request.form.get('phase2_data', '{}'))
            
            # Process uploaded files for comprehensive context
            files_dict = {
                'documents': request.files.getlist('documents'),
                'interviews': request.files.getlist('interviews'),
                'signals': request.files.getlist('signals')
            }
            
            if 'domain_map' in request.files:
                files_dict['domain_map'] = request.files['domain_map']
            
            # Extract comprehensive text context
            processor = initialize_processor()
            comprehensive_context = processor.extract_comprehensive_text(files_dict)
            
            # Generate Futures Triangle 2.0
            triangle_2_0 = processor.generate_futures_triangle_2_0(
                domain=domain,
                phase1_data=phase1_data,
                phase2_data=phase2_data,
                comprehensive_context=comprehensive_context
            )
            
            if 'error' in triangle_2_0:
                return jsonify({'error': triangle_2_0['error']}), 500
            
            return jsonify({
                'success': True,
                'futures_triangle_2_0': triangle_2_0
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-baseline-scenario', methods=['POST'])
    def generate_baseline_scenario():
        try:
            data = request.get_json()
            
            domain = data.get('domain', '').strip()
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            # Get Futures Triangle 2.0 data
            triangle_2_0_data = data.get('triangle_2_0_data', {})
            if not triangle_2_0_data:
                return jsonify({'error': 'Futures Triangle 2.0 data is required'}), 400
            
            # Optional Phase 1 data for context
            phase1_data = data.get('phase1_data', {})
            
            # Generate baseline scenario
            processor = initialize_processor()
            baseline = processor.generate_baseline_scenario(
                domain=domain,
                triangle_2_0_data=triangle_2_0_data,
                phase1_data=phase1_data
            )
            
            if 'error' in baseline:
                return jsonify({'error': baseline['error']}), 500
            
            return jsonify({
                'success': True,
                'baseline_scenario': baseline
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-driver-outcomes', methods=['POST'])
    def generate_driver_outcomes():
        try:
            data = request.get_json()
            domain = data.get('domain', '').strip()
            
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            # Get required data
            triangle_2_0_data = data.get('triangle_2_0_data', {})
            baseline_data = data.get('baseline_data', {})
            
            if not triangle_2_0_data:
                return jsonify({'error': 'Futures Triangle 2.0 data is required'}), 400
            if not baseline_data:
                return jsonify({'error': 'Baseline scenario data is required'}), 400
            
            # Optional Phase 1 data for context
            phase1_data = data.get('phase1_data', {})
            
            # Generate driver outcomes
            processor = initialize_processor()
            outcomes = processor.generate_driver_outcomes(
                domain=domain,
                triangle_2_0_data=triangle_2_0_data,
                baseline_data=baseline_data,
                phase1_data=phase1_data
            )
            
            if 'error' in outcomes:
                return jsonify({'error': outcomes['error']}), 500
            
            return jsonify({
                'success': True,
                'driver_outcomes': outcomes
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/generate-alternative-scenarios', methods=['POST'])
    def generate_alternative_scenarios():
        try:
            data = request.get_json()
            domain = data.get('domain', '').strip()
            
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400
            
            # Get scenario selections
            collapse_count = int(data.get('collapse_count', 0))
            new_equilibrium_count = int(data.get('new_equilibrium_count', 0))
            transformation_count = int(data.get('transformation_count', 0))
            
            selected_archetypes = {
                'Collapse': collapse_count,
                'New Equilibrium': new_equilibrium_count, 
                'Transformation': transformation_count
            }
            
            # Get required data
            baseline_data = data.get('baseline_data', {})
            driver_outcomes = data.get('driver_outcomes', {})
            triangle_2_0_data = data.get('triangle_2_0_data', {})
            
            if not baseline_data:
                return jsonify({'error': 'Baseline scenario data is required'}), 400
            if not driver_outcomes:
                return jsonify({'error': 'Driver outcomes data is required'}), 400
            
            # Generate scenarios
            processor = initialize_processor()
            scenarios = processor.generate_alternative_scenarios(
                domain=domain,
                selected_archetypes=selected_archetypes,
                baseline_data=baseline_data,
                driver_outcomes=driver_outcomes,
                triangle_2_0_data=triangle_2_0_data
            )
            
            if 'error' in scenarios:
                return jsonify({'error': scenarios['error']}), 500
            
            return jsonify({
                'success': True,
                'alternative_scenarios': scenarios
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    # Add this route to your app.py file (inside the create_app() function)

    @app.route('/api/wind-tunnel-analysis', methods=['POST'])
    def wind_tunnel_analysis():
        """Run Wind Tunnel policy stress testing against Phase 3 scenarios."""
        if processor is None:
            return jsonify({"error": "Server not initialized. Check GROQ_API_KEY."}), 500

        try:
            # Get form data
            domain = request.form.get('domain', '').strip()
            project_name = request.form.get('project_name', '').strip()
            
            if not domain:
                return jsonify({'error': 'Domain is required'}), 400

            # Get Phase 3 scenarios data
            try:
                phase3_data = json.loads(request.form.get('phase3_scenarios', '{}'))
            except json.JSONDecodeError:
                return jsonify({'error': 'Invalid Phase 3 scenarios data'}), 400

            if not phase3_data:
                return jsonify({'error': 'Phase 3 scenarios data is required'}), 400

            # Process uploaded policy files
            policy_files = request.files.getlist('policy_files')
            if not policy_files:
                return jsonify({'error': 'At least one policy document must be uploaded'}), 400

            # Extract text from all policy files
            policy_text = ""
            for policy_file in policy_files:
                try:
                    wrapper = FlaskFileWrapper(policy_file)
                    wrapper.seek(0)
                    extracted_text = processor.extract_text_from_file(wrapper)
                    policy_text += f"\n\n=== POLICY DOCUMENT: {policy_file.filename} ===\n"
                    policy_text += extracted_text
                    policy_text += "\n" + "="*50 + "\n"
                except Exception as e:
                    policy_text += f"\nError extracting from {policy_file.filename}: {str(e)}\n"

            if len(policy_text.strip()) < 100:
                return jsonify({'error': 'Could not extract sufficient text from policy documents'}), 400

            # Run Wind Tunnel analysis
            wind_tunnel_results = processor.run_wind_tunnel_analysis(
                domain=domain,
                policy_text=policy_text,
                phase3_scenarios=phase3_data,
                project_name=project_name
            )

            if 'error' in wind_tunnel_results:
                return jsonify({'error': wind_tunnel_results['error']}), 500

            return jsonify({
                'success': True,
                'wind_tunnel_analysis': wind_tunnel_results,
                'analyzed_files': [f.filename for f in policy_files],
                'policy_text_length': len(policy_text)
            })

        except Exception as e:
            app.logger.error(f"Wind Tunnel analysis error: {str(e)}")
            return jsonify({'error': f'Wind Tunnel analysis failed: {str(e)}'}), 500

# for translation
    def create_translation_service():
        """Initialize Google Cloud Translation service"""
        try:
            # Set your project ID
            project_id = "bsai-472610"  # Replace with your project ID
            
            # Make sure your Key.json is in the same directory as app.py
            app_path = os.path.dirname(__file__)
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f"{app_path}/Key.json"
            
            client = translate_v3.TranslationServiceClient()
            parent = f"projects/{project_id}/locations/global"
            
            return client, parent
        except Exception as e:
            print(f"Translation service initialization failed: {e}")
            return None, None

    # Add this new route
    # @app.route('/api/translate', methods=['POST'])
    # def translate_text():
    #     """Translate text from English to Lao"""
    #     try:
    #         data = request.get_json()
    #         text = data.get('text', '').strip()
    #         target_language = data.get('target_language', 'lo')  # 'lo' is Lao language code
            
    #         if not text:
    #             return jsonify({'error': 'No text provided'}), 400
            
    #         client, parent = create_translation_service()
    #         if not client:
    #             return jsonify({'error': 'Translation service not available'}), 500
            
    #         # Translate text
    #         response = client.translate_text(
    #             contents=[text],
    #             parent=parent,
    #             mime_type="text/plain",
    #             source_language_code="en",
    #             target_language_code=target_language,
    #         )
            
    #         translated_text = response.translations[0].translated_text if response.translations else text
            
    #         return jsonify({
    #             'success': True,
    #             'original_text': text,
    #             'translated_text': translated_text,
    #             'target_language': target_language
    #         })
            
    #     except Exception as e:
    #         return jsonify({'error': f'Translation failed: {str(e)}'}), 500


    @app.route('/api/translate', methods=['POST'])
    def translate_text_free():
        """Translate text using free Google Translate via deep_translator"""
        try:
            data = request.get_json()
            text = data.get('text', '').strip()
            target_language = data.get('target_language', 'lo')
            source_language = data.get('source_language', 'en')
            
            print(f"\n{'='*60}")
            print(f"[TRANSLATE API CALL]")
            print(f"  Source: {source_language} → Target: {target_language}")
            print(f"  Text length: {len(text)} chars")
            print(f"  Text: {text[:100]}..." if len(text) > 100 else f"  Text: {text}")
            print(f"{'='*60}")
            
            if not text:
                return jsonify({'error': 'No text provided'}), 400
            
            # Validate language codes
            if not isinstance(target_language, str) or len(target_language) != 2:
                return jsonify({'error': 'Invalid target language code'}), 400
            if not isinstance(source_language, str) or len(source_language) != 2:
                return jsonify({'error': 'Invalid source language code'}), 400
            
            try:
                # Check if already target language
                if target_language == source_language:
                    print(f"[SKIP] Source and target are same language: {source_language}")
                    return jsonify({
                        'success': True,
                        'original_text': text,
                        'translated_text': text,
                        'target_language': target_language,
                        'source_language': source_language
                    })
                
                translated_text = GoogleTranslator(
                    source=source_language,
                    target=target_language
                ).translate(text)
                
                print(f"[SUCCESS] Translated text: {translated_text[:100]}..." if len(translated_text) > 100 else f"[SUCCESS] Translated text: {translated_text}")
                
                return jsonify({
                    'success': True,
                    'original_text': text,
                    'translated_text': translated_text,
                    'target_language': target_language,
                    'source_language': source_language
                })
                
            except Exception as e:
                print(f"[ERROR] Translation failed: {str(e)}")
                return jsonify({'error': f'Translation failed: {str(e)}'}), 500
                
        except Exception as e:
            print(f"[ERROR] Request processing failed: {str(e)}")
            return jsonify({'error': f'Request processing failed: {str(e)}'}), 500

    # @app.route('/api/translate', methods=['POST'])
    # def translate_text_free():
    #     """Translate text using free Google Translate via deep_translator"""
    #     try:
    #         data = request.get_json()
    #         text = data.get('text', '').strip()
    #         # txttt = str(data)
    #         # txttt = txttt[:50]
    #         # print(f"DEEBAK:\n{txttt}\n")
    #         target_language = data.get('target_language', 'lo')
    #         source_language = data.get('source_language', 'en')  # Add this line
            
    #         if not text:
    #             return jsonify({'error': 'No text provided'}), 400
            
    #         # Validate language codes
    #         if not isinstance(target_language, str) or len(target_language) != 2:
    #             return jsonify({'error': 'Invalid target language code'}), 400
    #         if not isinstance(source_language, str) or len(source_language) != 2:
    #             return jsonify({'error': 'Invalid source language code'}), 400
            
    #         try:
    #             # Use deep_translator's GoogleTranslator
    #             translated_text = GoogleTranslator(
    #                 source=source_language,
    #                 target=target_language
    #             ).translate(text)
    #             print(f"\ntext:{text}\n")
    #             print(f"\nlen:{len(text)}\n")
    #             return jsonify({
    #                 'success': True,
    #                 'original_text': text,
    #                 'translated_text': translated_text,
    #                 'target_language': target_language,
    #                 'source_language': source_language
    #             })
                
    #         except Exception as e:
    #             return jsonify({'error': f'Translation failed: {str(e)}'}), 500
                
    #     except Exception as e:
    #         return jsonify({'error': f'Request processing failed: {str(e)}'}), 500


# working code paid
    # def translate_text():
    #     """Translate text from English to Lao"""
    #     try:
    #         data = request.get_json()
    #         text = data.get('text', '').strip()
    #         target_language = data.get('target_language', 'lo')
    #         mime_type = data.get('mime_type', 'text/plain')  # Add this line
            
    #         if not text:
    #             return jsonify({'error': 'No text provided'}), 400
            
    #         client, parent = create_translation_service()
    #         if not client:
    #             return jsonify({'error': 'Translation service not available'}), 500
            
    #         # Translate text
    #         response = client.translate_text(
    #             contents=[text],
    #             parent=parent,
    #             mime_type=mime_type,  # Use the provided mime_type
    #             source_language_code="en",
    #             target_language_code=target_language,
    #         )
            
    #         translated_text = response.translations[0].translated_text if response.translations else text
            
    #         return jsonify({
    #             'success': True,
    #             'original_text': text,
    #             'translated_text': translated_text,
    #             'target_language': target_language
    #         })
            
    #     except Exception as e:
    #         return jsonify({'error': f'Translation failed: {str(e)}'}), 500
    
    return app


app = create_app()


if __name__ == "__main__":
    # Run the Flask development server
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
